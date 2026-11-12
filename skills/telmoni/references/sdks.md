# SDK integration

Explicit instrumentation with a Telmoni SDK. The examples wrap an application's own functions (`invoke_provider`, `search_orders`); they call no model themselves. They follow the **current source** of the SDKs. The first published version, 0.2.0, differs: see [Versions](#versions), and read the installed package's own signatures before adapting any example.

## Contents

- [Versions](#versions)
- [The shape every language shares](#the-shape-every-language-shares)
- [Python](#python)
- [TypeScript / JavaScript](#typescript--javascript)
- [Go](#go)
- [Rust](#rust)
- [Beyond first instrumentation](#beyond-first-instrumentation)

## Versions

The registries serve 0.2.0 until a newer release is published; the current source is ahead of it. Check which you have installed (`pip show telmoni`, `npm ls telmoni`, `go list -m github.com/telmoni/telmoni/sdk/go`, `cargo tree -p telmoni`). For 0.2.0, change these things in the examples:

| In the examples | In 0.2.0 |
|---|---|
| A **trace**: `telmoni.trace(...)`, `Trace`, `TraceOptions`, the `trace=` argument | A **run**: `telmoni.run(...)`, `Run`, `RunOptions`, the `run=` argument. Python's `run(agent, user_id=, session_id=, tags=, sample_rate=)`; Go's `client.Run(ctx, agent, telmoni.RunOptions{...})` returning `*telmoni.Run`; Rust's `telmoni.run(agent, RunOptions)` |
| `prompt` and `prompt_version` on a model call | Not there: leave them out, and say the prompt is not recorded |
| `retrieval` | Not there in any SDK: record a search as a tool call |
| `Usage` with cache, reasoning and `cost` fields | Input, output, cache-read and cache-write tokens only |
| Rust `trace.model_call(...)?` | `run.model_call(...)` returns the guard itself, not a `Result`; `telmoni.run(...)` still returns one |
| `TELMONI_CAPTURE_CONTENT`, `TELMONI_SCRUB_SECRETS`, `TELMONI_SCRUB_PII` | Read by no SDK, and 0.2.0 has no scrubber: capture is the config field alone, off by default |

The span names on the wire are the same in both: `invoke_agent <agent>` for the root, `chat <model>` and `execute_tool <name>` inside it.

### Working forms for 0.2.0

Each of these ran against 0.2.0 and sent a root, a tool call and a model call with their token counts and no content. The application's own functions stand in for the provider. Messages are any JSON value: the SDK does not check their shape, and a list of `{role, content}` objects is the usual one.

Python (`pip install telmoni==0.2.0`). Add `logging.basicConfig(level=logging.WARNING)` if the application configures no logging, or the SDK's warnings are not shown:

```python
from telmoni import Telmoni, Usage

telmoni = Telmoni.from_env()          # once per process

def run_agent(question, customer):
    with telmoni.run("support-bot", user_id=customer):
        with telmoni.tool_call("search_orders", arguments={"customer": customer}) as tool:
            orders = search_orders(customer)
            tool.returned(orders)
        with telmoni.model_call(
            MODEL, provider="anthropic",
            input_messages=[{"role": "user", "content": question}],
        ) as call:
            reply = provider_chat(question)
            call.answered(
                response_model=reply["model"],
                usage=Usage(input_tokens=reply["input_tokens"], output_tokens=reply["output_tokens"]),
                output_messages=[{"role": "assistant", "content": reply["text"]}],
            )
        return reply["text"]

# at process teardown
telmoni.shutdown()
```

TypeScript (`npm install telmoni@0.2.0`; the signatures are in `node_modules/telmoni/dist/index.d.mts`, or `index.d.ts` under CommonJS):

```ts
import { Telmoni } from 'telmoni';

const telmoni = Telmoni.fromEnv();    // once per process

export async function runAgent(question: string, customer: string) {
  return telmoni.run('support-bot', { userId: customer }, async (run) => {
    const orders = await run.toolCall('search_orders', async (tool) => {
      const found = await searchOrders(customer);
      tool.returned(found);
      return found;
    });
    return run.modelCall(MODEL, { provider: 'anthropic' }, async (call) => {
      const reply = await providerChat(question);
      call.answered({
        responseModel: reply.model,
        usage: { inputTokens: reply.usage.inputTokens, outputTokens: reply.usage.outputTokens },
      });
      return reply.text;
    });
  });
}

// after short-lived work
if (!(await telmoni.flush())) console.warn('telmoni: a batch could not be sent');
// at process teardown
await telmoni.shutdown();
```

Go (`go get github.com/telmoni/telmoni/sdk/go@v0.2.0`; `go doc` shows the signatures). `Usage` holds plain integers, so leave `Usage` nil where the provider reported none rather than passing zeros:

```go
client, err := telmoni.NewFromEnv()   // once per process, in main
if err != nil { return err }
defer client.Shutdown(context.Background())

func runAgent(ctx context.Context, client *telmoni.Client, question, customer string) (string, error) {
	ctx, run := client.Run(ctx, "support-bot", telmoni.RunOptions{UserID: customer})
	defer run.End()

	toolCtx, tool := run.ToolCall(ctx, "search_orders", telmoni.ToolCallOptions{Arguments: customer})
	orders, err := searchOrders(toolCtx, customer)
	if err != nil {
		tool.Fail(err)
		tool.End()
		run.Fail(err)
		return "", err
	}
	tool.Returned(orders)
	tool.End()

	callCtx, call := run.ModelCall(ctx, MODEL, telmoni.ModelCallOptions{Provider: "anthropic", InputMessages: question})
	r, err := providerChat(callCtx, question)
	if err != nil {
		call.Fail(err)
		call.End()
		run.Fail(err)
		return "", err
	}
	call.Answered(telmoni.Answer{
		ResponseModel:  r.Model,
		Usage:          &telmoni.Usage{InputTokens: r.InputTokens, OutputTokens: r.OutputTokens},
		OutputMessages: r.Text,
	})
	call.End()
	return r.Text, nil
}
```

Rust (`cargo add telmoni@0.2.0`; the crate source is under `~/.cargo/registry/src`). Here `step`, `tool_call` and `model_call` return guards, not `Result`s; only `telmoni.run(...)` does. The `try_*_with` helpers take a closure that returns the application's own `Result`, annotated as `Ok::<_, E>(..)`, and record its error. `tool.returned(..)` takes a `String`, `&str` or `serde_json::Value`: leave it out unless the application already depends on `serde_json`.

```rust
use telmoni::{ModelCallOptions, Reply as ModelReply, RunOptions, Telmoni, ToolCallOptions, Usage};

fn run_agent(telmoni: &Telmoni, question: &str, customer: &str) -> Result<String, String> {
    let run = telmoni
        .run("support-bot", RunOptions { user_id: Some(customer.into()), ..RunOptions::default() })
        .map_err(|e| e.to_string())?;
    let result = (|| {
        let orders = run.try_tool_call_with("search_orders", ToolCallOptions::default(), |_tool| {
            Ok::<_, String>(search_orders(customer)?)
        })?;
        let reply = run.try_model_call_with(
            MODEL_NAME,
            ModelCallOptions { provider: Some("anthropic".into()), ..ModelCallOptions::default() },
            |call| {
                let reply = provider_chat(question, orders.len())?;
                call.answered(ModelReply {
                    response_model: Some(reply.model.clone()),
                    usage: Some(Usage {
                        input_tokens: Some(reply.input_tokens),
                        output_tokens: Some(reply.output_tokens),
                        ..Usage::default()
                    }),
                    ..ModelReply::default()
                });
                Ok::<_, String>(reply)
            },
        )?;
        Ok(reply.text)
    })();
    let result = run.on_result(result);   // marks the run failed on `Err`, returns it unchanged
    run.end();
    result
}

// in main: Telmoni::from_env() once; telmoni.flush() (a bool) after the work; telmoni.shutdown() at the end
```

## The shape every language shares

```text
client (one per process, from the environment)
└─ trace "support-bot"            one per agent execution; session id, user id, tags
   ├─ step "plan"                 optional, a meaningful stage
   │  └─ model call "<model>"     provider, prompt name and version; then the answer: response model, usage
   ├─ tool call "search_orders"   then what it returned, or its failure
   └─ retrieval "<source>"        then the documents found
flush after short-lived work; shut down once at process teardown
```

A trace's `user_id` and `session_id` are the application's own opaque ids, set only where the application has them. A model call's `prompt` and `prompt_version` name the prompt it used and are sent in every content mode, so they name a prompt, never a person. Messages, tool arguments and results, and retrieved documents are content: sent only with capture on and the project's content mode `on`. Passing them, or calling `returned`, is safe with capture off: the SDK drops the content.

## Python

Python 3.10+. Install `telmoni` with the project's package manager.

```python
from telmoni import Telmoni, Usage

telmoni = Telmoni.from_env()


def traced_run(question, session_id, user_id):
    with telmoni.trace("support-bot", session_id=session_id, user_id=user_id):
        with telmoni.model_call(
            model_name, provider="anthropic", prompt="triage", prompt_version="3"
        ) as call:
            reply = invoke_provider(question)
            call.answered(
                response_model=reply.model,
                usage=Usage(
                    input_tokens=reply.usage.input_tokens,
                    output_tokens=reply.usage.output_tokens,
                ),
            )
        with telmoni.tool_call("search_orders") as tool:
            orders = search_orders(reply)
            tool.returned(orders)
        return orders
```

- `trace`, `step`, `model_call`, `tool_call` and `retrieval` each work as a context manager, an async context manager and a decorator: `@telmoni.trace("support-bot")` over the execution's function is the smallest change.
- An exception that escapes a block marks its span failed and is re-raised.
- A decorated streaming function is covered through its iteration, not only its creation.
- `Usage` also takes `cache_read_input_tokens`, `cache_write_input_tokens`, `reasoning_output_tokens` and `cost`; `answered` takes `time_to_first_token` in seconds. Leave out what the provider did not report.
- `telmoni.flush()` returns `False` when a batch could not be sent; call it after short-lived work, and `telmoni.shutdown()` at process teardown. Warnings go to the `telmoni` logger.

Source: [Python SDK](https://github.com/telmoni/telmoni/blob/main/sdk/python/README.md).

## TypeScript / JavaScript

Node.js 18.19, or 20.6 and later. Install `telmoni` with the project's package manager, and keep it in server code.

```ts
import { Telmoni } from 'telmoni';

const telmoni = Telmoni.fromEnv();

async function tracedRun(question: string, sessionId: string, userId: string) {
  return telmoni.trace('support-bot', { sessionId, userId }, async (trace) => {
    const reply = await trace.modelCall(
      modelName,
      { provider: 'anthropic', prompt: 'triage', promptVersion: '3' },
      async (call) => {
        const answer = await invokeProvider(question);
        call.answered({
          responseModel: answer.model,
          usage: { inputTokens: answer.usage.inputTokens, outputTokens: answer.usage.outputTokens },
        });
        return answer;
      },
    );
    return trace.toolCall('search_orders', async (tool) => {
      const orders = await searchOrders(reply);
      tool.returned(orders);
      return orders;
    });
  });
}
```

- A trace and a step both open `step`, `modelCall`, `toolCall` and `retrieval`; the options argument may be left out.
- A callback returns the application's result and rethrows its failure. Await the work inside it: returning an unconsumed stream ends the span too soon.
- `usage` also takes `cacheReadInputTokens`, `cacheWriteInputTokens`, `reasoningOutputTokens` and `cost`; `answered` takes `timeToFirstToken` in seconds.
- `await telmoni.flush()` resolves `false` when a batch could not be sent; call it after short-lived work, and `await telmoni.shutdown()` at process teardown, once every trace has finished. Warnings go to `console.warn`.

Source: [TypeScript SDK](https://github.com/telmoni/telmoni/blob/main/sdk/typescript/README.md).

## Go

The module requires Go 1.26.10 or later: `go get` raises an older module's `go` directive to match, silently. Carry on, and say in the report that the project's Go toolchain and CI now need 1.26.10 or later. Install `github.com/telmoni/telmoni/sdk/go` with the project's module workflow.

```go
import (
	"context"

	telmoni "github.com/telmoni/telmoni/sdk/go"
)

func tracedRun(ctx context.Context, client *telmoni.Client, question, sessionID, userID string) error {
	ctx, tr := client.Trace(ctx, "support-bot", telmoni.TraceOptions{SessionID: sessionID, UserID: userID})
	defer tr.End()

	callCtx, call := tr.ModelCall(ctx, modelName, telmoni.ModelCallOptions{
		Provider: "anthropic", Prompt: "triage", PromptVersion: "3",
	})
	reply, err := invokeProvider(callCtx, question)
	if err != nil {
		call.Fail(err)
		call.End()
		tr.Fail(err)
		return err
	}
	call.Answered(telmoni.Answer{
		ResponseModel: reply.Model,
		Usage:         &telmoni.Usage{InputTokens: reply.InputTokens, OutputTokens: reply.OutputTokens},
	})
	call.End()

	toolCtx, tool := tr.ToolCall(ctx, "search_orders", telmoni.ToolCallOptions{})
	orders, err := searchOrders(toolCtx, reply)
	if err != nil {
		tool.Fail(err)
	} else {
		tool.Returned(orders)
	}
	tool.End()
	return err
}
```

- Create the client once at process scope with `telmoni.NewFromEnv()`, and `defer client.Shutdown(ctx)` in `main`; `client.Flush(ctx)` after short-lived work. Both return an `error`: check the flush's. Warnings go to `slog`; to send them elsewhere, build the client with `telmoni.New(telmoni.ConfigFromEnv(), telmoni.WithLogger(logger))` instead of `NewFromEnv`.
- `tr.Step`, `tr.ModelCall`, `tr.ToolCall` and `tr.Retrieval` each return a child context and a handle. Pass the child context to the work it covers, and the parent's to its siblings.
- A returned Go error is not seen by the SDK: call `Fail(err)` before `End()`. `Cancel()` marks a cancelled operation.
- End each handle where its work ends. A `defer` inside a long loop keeps every span open until the function returns.

Source: [Go examples](https://github.com/telmoni/telmoni/blob/main/sdk/go/example_test.go) and [implementation](https://github.com/telmoni/telmoni/tree/main/sdk/go).

## Rust

Rust 1.88+. Add the `telmoni` crate with the project's dependency workflow.

```rust
// `Reply` may collide with the application's own type: alias it if it does.
use telmoni::{ModelCallOptions, Reply, Telmoni, ToolCallOptions, TraceOptions, Usage};

// MODEL_NAME is the model the application requests, known before the call;
// the response's own model name goes in `response_model` after it.
fn traced_run(telmoni: &Telmoni, question: &str, session_id: &str) -> Result<(), telmoni::Error> {
    let trace = telmoni.trace(
        "support-bot",
        TraceOptions {
            session_id: Some(session_id.into()),
            ..TraceOptions::default()
        },
    )?;
    {
        let call = trace.model_call(
            MODEL_NAME,
            ModelCallOptions {
                provider: Some("anthropic".into()),
                prompt: Some("triage".into()),
                prompt_version: Some("3".into()),
                ..ModelCallOptions::default()
            },
        )?;
        let reply = invoke_provider(question);
        call.answered(Reply {
            response_model: Some(reply.model),
            usage: Some(Usage {
                input_tokens: Some(reply.input_tokens),
                output_tokens: Some(reply.output_tokens),
                ..Usage::default()
            }),
            ..Reply::default()
        });
    }
    let tool = trace.tool_call("search_orders", ToolCallOptions::default())?;
    search_orders(question);
    drop(tool); // ends the tool call's span; `returned(..)` would add its result as content
    trace.end();
    Ok(())
}
```

- Create the client once with `Telmoni::from_env()`; `telmoni.flush()` (a `bool`: `false` means a batch was not sent) after short-lived work, `telmoni.shutdown()` at process teardown, after every child and root has ended. Warnings go through `tracing::warn!` under the target `telmoni`, so they show only if the application has a `tracing` subscriber.
- Every handle is a guard: its span ends when it drops or on `end()`.
- Nothing marks a failure by itself: call `fail("ErrorType")` or `cancel()`, or use the `try_*_with` closure helpers and `on_result`, which record an error and hand it back unchanged.
- Across an `await`, keep the handle alive and follow the SDK's context guidance (`attach`, `FutureExt::with_context`); never hold an attached thread-local guard across an await.

Source: [Rust SDK](https://github.com/telmoni/telmoni/blob/main/sdk/rust/README.md).

## Beyond first instrumentation

Read the chosen SDK's README for these, only when the user asks for them:

- **Across services:** inject and extract, so a downstream service's work joins the trace.
- **A trace recorded after it ended:** from a log or a queue. It needs a stable, nonzero 32-hex trace id and valid times, and is no substitute for live tracing.
- **Scores:** a number or a label on a trace or a span.
- **Content masks:** the application's own function over content before it leaves.
- **The guard:** step and spend caps that stop a trace. They change how the application runs, so never add them as part of ordinary tracing.

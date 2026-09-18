# Python Logging

Python logging call and configuration mechanics.

Obtain one module-scoped logger through the project-owned logging facade. When
the standard library is the established facade, use
`logging.getLogger(__name__)`. Do not invent a second wrapper or call
`basicConfig` from a reusable library module.

Pass message values as arguments instead of building an f-string or calling
`format`; deferred formatting avoids work when the record is disabled:

```python
logger.debug("loaded %s records for batch %s", count, batch_id)
```

Inside an exception handler, attach the active traceback with `logger.exception`
or the facade's `exc_info` mechanism. Do not flatten it into the message. Use
the facade's supported structured-field mechanism instead of embedding parseable
key-value syntax in free text.

Configure handlers, sinks, and levels once at the application composition root.
Library code emits records and leaves policy to the embedding application. Use
`print` only for an intentional command-line output contract, not as application
logging.

Finish when every new call uses the owned facade, defers interpolation, and
attaches an active traceback through the mechanism the configured logging stack
understands.

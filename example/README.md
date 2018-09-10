# Example Site

This is a very simple example site demonstrating how to mix templates and content.

The [base.html](templates/base.html) template includes both the [header.html](templates/header.html)
and the [footer.html](templates/footer.html) template.

The [index.html](content/index.html) content extends [base.html](templates/base.html)
to demonstrate the power and flexibility of [Tornado's](http://tornadoweb.org) templating
engine.

## Building the example

After installing `landspout` run the `landspout` command in this directory (`./example`):

```bash
landspout -d dist build
```

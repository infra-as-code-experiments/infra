# infra

Infrastructure as code configuration


## How to setup

1. Install `pulumi` binary with `curl -fsSL https://get.pulumi.com/ | sh`
2. Run `pulumi new`. Log in via browser and choose a template. I started with `github-python`.
3. Follow the wizard steps.

After the step-by-step setup, I noticed a couple things that felt unusual in a conda context:

- `pulumi` handles its own `venv` when you choose a Python template. It will symlink to the
current `python` in `PATH`. Instead, we have chosen to bootstrap the environment with `pixi` so
a random interpreter is not chosen on initialization. You just need to run `pixi install`. We
have adjusted the `runtime.options.virtualenv` path in `Pulumi.yaml` accordingly. You can also 
change this to a given conda environment if you want, but I'm not sure if one can use env vars here.
- The Pulumi "programs" (e.g. `__main__.py`) are located in the repository root by default.
  I think it's tidier to have them under a subdirectory like `src/`. This was adjusted in
  `Pulumi.yaml` by changing the value of `main`.

> I think Pulumi will still write to `requirements.txt` here and there, so we have to find a way
of keeping `pixi.toml` in sync to benefit from the lockfiles.

Once there we can start importing repositories, teams and other github resources

## Import Github resources

> We need `pulumi-github` in the virtual environment. This should have been added by the `pulumi
> new` command already.

> This follows https://www.pulumi.com/blog/managing-github-with-pulumi/ with some changes.


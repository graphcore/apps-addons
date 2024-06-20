Introduction
------------

The Examples benchmarking tool is a sub-module of Graphcore's `Examples-utils https://github.com/graphcore/examples-utils`_ package, designed to simplify and automate the process of running the benchmarks provided with the various examples in Graphcore's `Examples repository https://github.com/graphcore/examples`_.

At its simplest, all that's required to  use the tool and and the extensive default functionality is:
```
python3 -m examples_utils benchmark
```
From the root dir of the example to benchmark. The `examples_utils` package is automatically installed when any example's requirements are installed, and so no setup is required to use this.

For users who are new to running such examples or just wish to run examples without any manual customisation of the examples/environment, the benchmaring tool provides a very simple and quick interface for getting the examples to run using the verified and tested benchmarks. For these use cases, the following functionality is made available:
- Setting up the environment and directories requiredfor running and monitoring examples
- Recording and analysing outputs and metrics from the examples to provide key performance indicators from the examples
- Automating checkpoint syncing, early exits on compilation and exporting results all from one line
And much more.

More experienced users of the examples provided in Graphcore's `Examples repository https://github.com/graphcore/examples`_ will not necessarily need to use this benchmarking tool, but may still choose to due to the wide range of features that streamline and organise much of the setup and repetition required for running larger (multiple host machines) benchmarks or multiple benchmarks in sequence. To this end, the benchmarking tool provides options for:
- Automatically syncing code, SDK, and virtual environment directories across specified host machines as well as the corresponding clean-up
- Neatly organising the running and output logs/metrics from multiple benchmarks run at once
- Handling the requirements installation steps for all benchmarks run across all hosts
To name a few.

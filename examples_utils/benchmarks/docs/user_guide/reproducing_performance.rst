Reproducing performance
------------

Graphcore provides performance metrics (throughput and latency being the primary ones) for all benchmarked examples on the `performance results https://www.graphcore.ai/performance-results`_ page, updated at every major event and SDK release. The benchmarking tool allows users to quickly and easily reproduce these performance results.

Prerequisites:
- Setup the system for using Graphcore's IPUs
- Have the Poplar SDK installed and enabled
- Install the example's requirements in a python environment

For more information on the pre-requisites, please follow the `quick start guides https://docs.graphcore.ai/en/latest/getting-started.html`_ provided `

Running the Benchmarks
The user can use the following command to run the benchmarks:

The benchmarking tool provided by Graphcore allows users to recreate the performance numbers provided by Graphcore by running the same benchmarks on their own systems. This allows users to ensure that their systems are configured correctly and to identify any issues that may affect performance. The tool also allows users to compare their results with the Graphcore's published performance numbers, which can be useful in identifying any performance issues and in determining the cause of any discrepancies.
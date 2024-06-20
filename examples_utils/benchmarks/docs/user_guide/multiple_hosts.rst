Introduction

In some cases, benchmarks may require more computational resources than can be provided by a single host. In these situations, it is necessary to use multiple hosts to run the benchmark. This module provides an easy way to set up and run benchmarks on multiple hosts, ensuring that the hosts are configured correctly and that the necessary code and data are present on all hosts.

Prerequisites

To use this module, you will need to have multiple hosts available, each with the appropriate computational resources (255 AMD vCPUs and ~500GB ram etc).
The hosts must be running a compatible operating system and have the necessary dependencies installed.
The hosts must be able to communicate with each other via IP addresses.
Setting up the hosts

Before using this module, you will need to set up the hosts as follows:

Make sure that the same version of the code is installed on all hosts.
Ensure that the necessary data is available on all hosts.
Make sure that the necessary environment variables are set on all hosts.
To use this module, you will also need to provide the IP addresses of all the hosts to the module when running the benchmark.

Running the benchmark

Once the hosts are set up, you can use this module to run the benchmark on multiple hosts.

The module will automatically configure the hosts, ensuring that the necessary code and data are present on all hosts, and that the environment variables are set correctly.

The module will also use the IP addresses provided to set up communication between the hosts.

Example of how to use the module:

Copy code
    from multiple_hosts_module import BenchmarkRunner

    # Initialize the BenchmarkRunner
    runner = BenchmarkRunner(host_ips=["192.168.1.100", "192.168.1.101"])

    # Run the benchmark
    runner.run_benchmark("benchmark_name")
Conclusion

This module makes it easy to set up and run benchmarks on multiple hosts. It ensures that the hosts are configured correctly and that the necessary code and data are present on all hosts. It also facilitates communication between the hosts by allowing you to pass the IP addresses of all the hosts when running the benchmark.

References

For more information on how to use this module, please refer to the inline documentation and the examples provided in the module.
For more information on how to run benchmarks on multiple hosts, please refer to the Graphcore documentation
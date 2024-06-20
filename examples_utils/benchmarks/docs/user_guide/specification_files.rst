Introduction:

Specification files are written in YAML format and are used to define the parameters and settings for running benchmarks on different models and datasets.
File Structure:

Each specification file consists of a series of key-value pairs that define the different options and settings for the benchmark.
The file begins with a top-level key, 'train_options', which contains a set of default options that are common to all benchmarks.
Under the 'train_options' key, there are several subkeys:
'env': This key is used to specify environment variables that should be set before running the benchmark. In this example, the 'TF_POPLAR_FLAGS' variable is set to '--executable_cache_path=/tmp/tf_cache/'
'data': This key is used to specify the data that the benchmark will run on. In this example, the 'throughput' key is used to specify a regular expression that will be used to extract the throughput from the benchmark's output.
'output': This key is used to specify the format of the benchmark's output. In this example, the benchmark will output the 'samples/sec' and 'throughput' values.
Benchmark Definitions:

Following the 'train_options' key, individual benchmarks are defined using a unique key. In this example, the benchmark is called 'tf2_cluster_gcn_ppi_train_real_pod4'.
Each benchmark definition contains several subkeys:
'<<: *train_options': This key is used to inherit the default options from the 'train_options' key.
'description': This key is used to provide a brief description of the benchmark.
'cmd': This key is used to specify the command that should be run to execute the benchmark. In this example, the benchmark is run using the 'poprun' command and the 'run_cluster_gcn.py' script. Additional parameters are passed to the script to specify the dataset, number of epochs, and other settings.
Conclusion:

Benchmark specification files provide a way to define and run benchmarks on different models and datasets in a consistent and reproducible way.
With the use of these specification files, it's easy to modify and add new benchmarks without the need to change the code.
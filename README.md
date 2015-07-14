# Fiware MkDocs site builder

This repository contains the custom [MkDocs](http://www.mkdocs.org/) site builder script used by Fiware.

## Description

The repository is structured as it follows:

* **conf**: Folder containing the configuration file for the script.
    * **mkdocs-builder.yml**: Configuration file for the script. Currently, it will be created on the first execution of the script and the only variable that can be edited is 'default_theme_folder'. 
* **custom_theme**: Fiware custom theme goes here.  Currently, this folder is a copy of <https://github.com/FiwareULPGC/Fiware-MkDocs-template>.
* **mkdocs-builder.py**: The script source code.

## Features

* Single site compilation.
* Multiple site compilation.
* Ability to configure a default custom theme.

## Requirements

The software requirements for the script are:

* Python 2.7

* Python libraries:
    * scriptine
    * sh
    * pyyaml

* MkDocs: [Installation instructions](http://www.mkdocs.org/#installation)

The script has been developed and tested under Ubuntu 14.04 OS.

## How to execute mkdocs-builder

From now on, we will refer to the location of the cloned **mkdocs-builder** folder as '/home/fiware_developer/mkdocs-builder'.

Once you have cloned the **mkdocs-builder** repository, you have three options to use the script:

* Simply move inside the cloned repository folder ('/home/fiware_developer/mkdocs-builder') and execute like ```$ ./mkdocs-builder.py -h```
* Use **python** command as ```$ python /home/fiware_developer/mkdocs-builder/mkdocs-builder.py -h``` 
* You could create an alias using ```$ alias -p mkdocs-builder="python /home/fiware_developer/mkdocs-builder/mkdocs-builder.py"```. From that point on you can execute ```$ mkdocs-builder -h```.

In the rest of the instructions we will use the third approach for the sake of brevity.

## How to work with mkdocs-builder

Some relevant notes:

* The first time the script is executed, the configuration file will be created and saved inside the conf folder.

The execution options for the script are:

* Display script help: ```$ mkdocs-builder -h```
* Display or change configuration: ```$ mkdocs-builder config```
* Compile a single site in MkDocs: ```$ mkdocs-builder compile <folder_to_compile>```
* Compile a multiple site in MkDocs: ```$ mkdocs-builder compile-multi <folder_to_compile>```

In the following sections we will explain more the previous commands. In order to follow the examples, bear in mind that we have cloned the single site and multi-site example repositories in '/home/fiware_developer/single-site' and '/home/fiware_developer/multi-site' respectively.

### Display help
Whenever you forget the option available in mkdocs-comiler, simply run the help command and the following output will display:

```
$ mkdocs-builder -h
Usage: mkdocs-builder.py command [options]

Options:
  -h, --help  show this help message and exit

Commands:
  compile        Compile a repository documentation using MkDocs.
  config         Commmand to allow to read/write configuration variables. 
  compile-multi  Compile a repository documentation into a multiple folder site using MkDocs.

```

### Configuration related commands

The **config** command will display the current configuration for the script when invoked without arguments:

``` 
$ mkdocs-builder config
Not editable variables:
     - conf_folder:  /home/fiware_developer/mkdocs-builder/conf/
     - build_folder:  /home/fiware_developer/mkdocs-builder/.tmp_build/
Editable variables:
	 - default_theme_folder:  /home/fiware_developer/mkdocs-builder/custom_theme/
```

If **value** and **config-variable** are passed during invocation, the variable will get updated with the specified value:

```
$ mkdocs-builder config --value='/home/fiware_developer/custom_theme' --config-variable='default_theme_folder'

$ mkdocs-builder config
Not editable variables:
	 - conf_folder:  /home/fiware_developer/mkdocs-builder/conf/
	 - build_folder:  /home/fiware_developer/mkdocs-builder/.tmp_build/
Editable variables:
	 - default_theme_folder:  /home/fiware_developer/custom_theme
```

### Single site compilation command

In order to compile a site using **mkdocs-builder** simply run ``` $ mkdocs-builder compile <repository_to_compile_folder> ```. Using the examples provided, the result in the terminal would look like :

```
$ mkdocs-builder compile /home/fiware_developer/single-site/
INFO     -  Compiling /home/fiware_developer/single-site
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/compiled_sites/Demo_single_site_2015-07-13_12-54-20 
WARNING -  The page "index.md" contained a hyperlink to "../user/archivo.md" which is not listed in the "pages" configuration. 

INFO 	-  End of site compilation

```
Since we didn't tell the command an output directory, the site will be compiled under *compiled_sites/\<name_of_the_single-site><compilation_timestamp\>*:
```
$ ls compiled_sites/Demo_single_site_2015-07-13_12-54-20/
css  fonts  img  index.html  js  license  mkdocs  search.html  sitemap.xml
```
We can also tell the script to compile into a desired folder with the argument **--output_folder**
```
$ mkdocs-builder compile /home/fiware_developer/single-site/ --output-folder=./custom_out_folder_single-site
INFO     -  Compiling /home/fiware_developer/single-site
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/custom_out_folder_single-site 
WARNING -  The page "index.md" contained a hyperlink to "../user/archivo.md" which is not listed in the "pages" configuration. 

INFO 	-  End of site compilation

```
The compiled site will be in the expected folder:
```
$ ls custom_out_folder_single-site/
css  fonts  img  index.html  js  license  mkdocs  search.html  sitemap.xml

```

### Multiple site compilation command

In order to compile a multi site using **mkdocs-builder** simply run ``` $ mkdocs-builder compile-multi <repository_to_compile_folder> ```. Using the examples provided, the result in the terminal would look like :


```
$ mkdocs-builder compile-multi /home/fiware_developer/multi-site
INFO     -  Compiling /home/fiware_developer/multi-site
INFO 	-  Ignoring 'theme_dir' attribute especified in config file '/home/fiware_developer/multi-site/mkdocs.yml'.
	   Using default value ['theme_dir': '/home/postgis/custom_theme/']. 
INFO 	-  Ignoring 'site_dir' attribute especified in config file '/home/fiware_developer/multi-site/mkdocs.yml'.
	   Using default value: ['site_dir': '/home/fiware_developer/results/compiled_sites/multi_site_demo_2015-07-13_12-59-49'].
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/main/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/main
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/admin/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/admin
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/test-list/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/test-list
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/user/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/user

INFO 	-  Showing output for 'Orion Context Broker' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/compiled_sites/multi_site_demo_2015-07-13_12-59-49/main 

INFO 	-  Showing output for 'Admin Guide' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/compiled_sites/multi_site_demo_2015-07-13_12-59-49/admin 

INFO 	-  Showing output for 'User Guide' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/compiled_sites/multi_site_demo_2015-07-13_12-59-49/user 

INFO 	-  Showing output for 'Testing Lists CSS' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/compiled_sites/multi_site_demo_2015-07-13_12-59-49/test-list 
WARNING -  The page "index.md" contained a hyperlink to "../user/archivo.md" which is not listed in the "pages" configuration. 
INFO 	-  End of multisite compilation


```

Since we didn't tell the command an output directory, the site will be compiled under *compiled_sites/\<name_of_the_multi-site><compilation_timestamp\>*:
```
$ ls compiled_sites/multi_site_demo_2015-07-13_12-59-49/
admin  css  fonts  img  index.html  js  license  main  mkdocs  README.md~  search.html  sitemap.xml  test-list  user
```

And we can also tell the script to compile into a desired folder with the argument **--output_folder**

```
$ mkdocs-builder compile-multi /home/fiware_developer/multi-site --output-folder=./custom_out_folder_multi-site
INFO     -  Compiling /home/fiware_developer/multi-site
INFO 	-  Ignoring 'theme_dir' attribute especified in config file '/home/fiware_developer/multi-site/mkdocs.yml'.
	   Using default value ['theme_dir': '/home/postgis/custom_theme/']. 
INFO 	-  Ignoring 'site_dir' attribute especified in config file '/home/fiware_developer/multi-site/mkdocs.yml'.
	   Using default value: ['site_dir': '/home/fiware_developer/results/custom_out_folder_multi-site'].
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/main/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/main
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/admin/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/admin
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/test-list/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/test-list
INFO 	-  Calling compiling for subsite '/home/fiware_developer/multi-site/doc/manuals/user/'
INFO 	-  Compiling /home/fiware_developer/multi-site/doc/manuals/user

INFO 	-  Showing output for 'Orion Context Broker' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/custom_out_folder_multi-site/main 

INFO 	-  Showing output for 'Admin Guide' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/custom_out_folder_multi-site/admin 

INFO 	-  Showing output for 'User Guide' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/custom_out_folder_multi-site/user 

INFO 	-  Showing output for 'Testing Lists CSS' subsite compilation
INFO    -  Cleaning site directory 
INFO    -  Building documentation to directory: /home/fiware_developer/results/custom_out_folder_multi-site/test-list 
WARNING -  The page "index.md" contained a hyperlink to "../user/archivo.md" which is not listed in the "pages" configuration. 
INFO 	-  End of multisite compilation

```

The compiled site will be in the expected folder:
```
$ ls custom_out_folder_multi-site/
admin  css  fonts  img  index.html  js  license  main  mkdocs  README.md~  search.html  sitemap.xml  test-list  user
```

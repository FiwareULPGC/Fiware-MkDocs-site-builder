#! /usr/bin/env python

def convert_to_md(src, dest, src_ext):
  """ Utility to convert from the desired input format to markdown. It will also change links inside the file. """
  print "INFO\t-  Converting file %s to markdown syntax." % src

  # Compile the command
  markdown_dest = dest.replace("."+src_ext, ".md")

  if src_ext == 'rst':
    from_format = 'rst'    

  command = ["pandoc", "--from="+from_format, "--to=markdown", "--output=%s"%markdown_dest, src]
  subprocess.Popen(command, stderr=subprocess.PIPE).communicate()

  # Find the links to be changed in the newly converted file and cahnge them to md references
  with open(markdown_dest, "r") as infile:
    content = infile.read()

  regex_str="\[(.+)\]\((.+)\."+src_ext+"(#.*)?\)"
  reference_regex = re.compile(regex_str)

  references_to_change = reference_regex.findall(content)

  if references_to_change:
    for reference in references_to_change:
      link_text = reference[0]
      page      = reference[1]
      section   =  reference[2]
      
      original_ref = "[%s](%s%s)" % ( link_text, page+"."+src_ext, section)
      new_ref = "[%s](%s%s)" % ( link_text, page+".md", section)

      content = content.replace(original_ref, new_ref)

    with open(markdown_dest, "w") as outfile:
      outfile.write(content)

# end convert_to_md

def copy_convert(src, dest):
  """ Utility to copy repo files and folders. When a file is not in markdown format, we make a conversion instead of a plain copy. """
  try:
    shutil.copytree(src, dest)
  except OSError as e:
    # If the error was caused because the source wasn't a directory
    if e.errno == errno.ENOTDIR:
      if dest.split(".")[-1] == "rst":
        convert_to_md(src, dest, 'rst')
      else:
        shutil.copy(src, dest)
    elif e.errno == errno.EEXIST:

      return
    else:
      print('WARNING\t-  Directory not copied. Error: %s' % e)
# end copy_convert

def step( source_target_root_folders, dirname, names ):
  # Ignore .git and .gitignore folders
  if dirname.find("/.git") != -1:
    return

  source_root_folder = source_target_root_folders[0]
  target_root_folder = source_target_root_folders[1]
  
  for name in names:
    # Substitute README files for index version
    if os.path.basename(name).split('.')[0] == 'README':
      target_name=name.replace("README", "index")
    else: 
      target_name = name

    src = os.path.normpath( os.path.join( source_root_folder, dirname, name ) )
    dest = os.path.normpath( os.path.join( target_root_folder, dirname, target_name ) )

    copy_convert( src, dest )
# end step

def change_pages_extension( pages ):
  """ Utility to normalise index configuration pages into md files """
  out_pages=[]

  for i in xrange(len(pages)):
    out_name = {}
    for name in pages[i]:
      try:
        if pages[i][name].split(".")[-1]=="rst":
          out_name[name] = pages[i][name].replace(".rst", ".md")
        else:
          out_name[name] = pages[i][name]

        if pages[i][name].split(".")[0]=="README":
          out_name[name] = "index.md"

      # Call recursively if a list of subpages is found
      except AttributeError as e:
        out_name[name] = change_pages_extension( pages[i][name] ) 

      out_pages.append( out_name )

  return out_pages
# end change_pages_extension

def clean_duplicate_lines(lines):
  """ Utility to clean duplicate lines from a list """
  seen = set()
  return [x for x in lines if x not in seen and not seen.add(x)]

def normalise_folder_paths(folder_paths):
  """Utility to deal with final slashes in folder paths. Paths will be returned with the sufix '/'."""

  if isinstance( folder_paths, basestring ):
    if folder_paths[-1]=='/':
      out = folder_paths
    else:
      out = folder_paths+'/' 

  else:
    out = []
    for folder_path in folder_paths: out.append( normalise_folder_paths( folder_path ) )

  return out
#end normalise_folder_paths

def replace_broken_links( compiled_subsite_root_folder, subsite_name, subsites, links_to_replace ):
  """Utility to rewrite links that break between different MkDocs subsites in a multisite compilation."""

  compiled_subsite_root_folder = normalise_folder_paths( compiled_subsite_root_folder )

  for page in links_to_replace:
    if page == 'index.md':
      file_to_edit = compiled_subsite_root_folder+"/index.html"
    else:
      file_to_edit = compiled_subsite_root_folder+page.split('.md')[0]+"/index.html"


    with open (file_to_edit, "r") as f: data=f.read()

    for link in links_to_replace[page]:
      corrected_link = link.split('.md')[0]
      data = data.replace( link, corrected_link )

    with open (file_to_edit, "w") as f: f.write( data )
#end replace_broken_links

def compiled_file_exists( compiled_subsite_root_folder, file_relative_path, md_link ):
  
  compiled_subsite_root_folder = normalise_folder_paths( compiled_subsite_root_folder )

  if file == "index.md":
    compiled_subsite_page_path = compiled_subsite_root_folder
  else:
    pos = file_relative_path.find("/")
    if pos == -1:
      file_relative_path = ''
    else:
      file_relative_path = file_relative_path[0:pos]
    compiled_subsite_page_path = compiled_subsite_root_folder+file_relative_path

  compiled_subsite_page_folder_path = normalise_folder_paths( path.dirname( compiled_subsite_page_path ) )

  relative_html_link = md_link.split('.md')[0]+"/index.html"

  return path.isfile( compiled_subsite_page_folder_path+relative_html_link )

#end compiled_file_exists

def compile_single(repo_path, extra_conf=None, output_folder=None):
  """ Function to compile a single MkDocs site. """

  # Delete mkdocs.yml symlink if it exsits
  if path.isfile(build_folder+"mkdocs.yml"):
    sh.rm(build_folder+"mkdocs.yml")

  # Delete docs folder if it already exists
  if path.exists(build_folder+"docs"):
    sh.rm("-r", build_folder+"docs/")
  
  sh.mkdir("-p", build_folder+"docs")

  # Take out the last slash if it exists
  if repo_path[-1]=='/':
    repo_path = repo_path[:-1]

  print "INFO \t-  Compiling %s" % repo_path

  if not path.isfile(repo_path+"/mkdocs.yml"):
    print 'ERROR \t-  mkdocs.yml file not found in path %s. Please, check that the path you are providing leads to the root file of the repo.' % repo_path
    return

  # We get the absolute path to the repository to construct the symlinks
  repo_path = path.abspath(repo_path)

  # Here we load the original MkDocs config file and make the needed changes to compile the site automatically
  with open(repo_path+"/mkdocs.yml", "r") as stream:
    conf = yaml.load(stream)

  if "theme_dir" in conf:
    print "INFO \t-  Ignoring 'theme_dir' attribute especified in config file '%s'.\n\t   Using default value ['theme_dir': '%s']. " % \
      ( repo_path+"/mkdocs.yml", default_theme_folder )
  conf["theme_dir"] = default_theme_folder 

  site_name = conf['site_name'].replace(" ", "_")

  if output_folder is None:
    compiled_site_root_folder = path.abspath( "compiled_sites/"+site_name+"_"+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'+"/") )
  else:
    compiled_site_root_folder = path.abspath( output_folder )

  if "site_dir" in conf:
    print "INFO \t-  Ignoring 'site_dir' attribute especified in config file '%s'.\n\t   Using default value: ['site_dir': '%s']." % \
      ( repo_path+"/mkdocs.yml", compiled_site_root_folder )
  conf["site_dir"] = compiled_site_root_folder


  if "pages" in conf:
    conf["pages"] =  change_pages_extension(conf["pages"])


  if extra_conf:
    conf["subsites"]=[]
    
    if "landing_page" in extra_conf:
      conf["landing_page"]=extra_conf["landing_page"]

    for subsite_name in extra_conf["subsites"]:
      conf["subsites"].append( { subsite_name: extra_conf["subsites"][subsite_name].split("/")[-2] } )

  with open(build_folder+"mkdocs.yml", 'w') as outfile:
    outfile.write( yaml.dump(conf, default_flow_style=False) )


  # Delete the compiled site folder if it already exists
  if output_folder is None and path.exists(compiled_site_root_folder):
    sh.rm("-r", compiled_site_root_folder)
  
  sh.mkdir("-p", compiled_site_root_folder)

  # Copy or convert (if not in markdown) the files from the original repo to the build directory
  source_path=repo_path
  target_path=build_folder+'docs'

  origin_directory = str( sh.pwd() ).rstrip('\n')
  sh.cd( source_path )

  os.path.walk('./', step, [source_path, target_path])

  sh.cd( origin_directory )

  origin_directory = str( sh.pwd() ).rstrip('\n')

  sh.cd( build_folder )

  # The return value will be the error output from MkDocs
  [ _, execution_output ] = subprocess.Popen(["mkdocs", "build", "--clean"], stderr=subprocess.PIPE).communicate()

  sh.cd( origin_directory )

  return execution_output
#end compile_single


def compile_command(repo_path, output_folder=None):
  """Compile a repository documentation using MkDocs."""

  repo_path = path.abspath( repo_path )
  if output_folder: output_folder = path.abspath( output_folder )

  print compile_single( repo_path , None, output_folder )
  print "INFO \t-  End of site compilation\n"
#end compile_command

def compile_multi_command(repo_path, output_folder=None):
  """Compile a repository documentation into a multiple folder site using MkDocs."""

  # Delete mkdocs.yml symlink if it exsits
  if path.isfile(build_folder+"mkdocs.yml"):
    sh.rm(build_folder+"mkdocs.yml")

  # Delete docs folder if it already exists
  if path.exists(build_folder+"docs"):
    sh.rm("-r", build_folder+"docs/")

  sh.mkdir("-p", build_folder+"docs")

  # Check the  that the mkdocs yml file is found in the provided repo path before continuing
  repo_path = normalise_folder_paths( path.abspath( repo_path ) )

  if not path.isfile(repo_path+"mkdocs.yml"):
    print 'ERROR \t-  mkdocs.yml file not found in path %s. Please, check that the path you are providing leads to the root file of the repo.' % repo_path
    return

  # We get the absolute path to the repository to construct the symlinks
  repo_path = path.abspath( repo_path )
  repo_path = normalise_folder_paths( repo_path )

  # Do not copy the theme_dir nor site_dir variables
  open(build_folder+"mkdocs.yml",'w').writelines([ line for line in open(repo_path+"/mkdocs.yml") if not 'theme_dir:' in line and not 'site_dir:' in line])

  # Load the main yml file to get site name and subsites paths
  with open(build_folder+"mkdocs.yml", "r") as stream:
    conf = yaml.load(stream)
  
  site_name = conf['site_name'].replace(" ", "_").lower()

  if output_folder is None:
    compiled_site_root_folder = "compiled_sites/"+site_name+"_"+datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

  else:
    compiled_site_root_folder = path.abspath( output_folder )

  # Delete the site compiled folder if it already exists
  if  path.exists(compiled_site_root_folder):
    sh.rm("-r", compiled_site_root_folder)
  
  compiled_site_root_folder = normalise_folder_paths( compiled_site_root_folder )

  sh.mkdir("-p", compiled_site_root_folder)

  subsites_dir = normalise_folder_paths( conf['subsites_dir'] )

  subsites_dirs=[]
  for dir_name, subdir_list, file_list in os.walk(repo_path+subsites_dir):
    for dirname in subdir_list:
      subsites_dirs.append( subsites_dir+dirname )
    break

  subsites_dirs=normalise_folder_paths( subsites_dirs )

  # Get the name of the subsites
  subsites = {}
  for subsite_path in subsites_dirs:
    aux_dict = {}

    if not path.isfile(str(repo_path+subsite_path)+"mkdocs.yml"):
      print 'ERROR \t-  mkdocs.yml file not found in path \'%s\'. Please, check that the path you are providing leads to the root file of the desired subsite.' % (repo_path+subsite_path)
      return
    #

    with open(str(repo_path+subsite_path)+"mkdocs.yml", "r") as stream:
      local_conf = yaml.load(stream)

    if 'site_name' in local_conf:
      subsite_name = local_conf['site_name']
    else:
      print 'ERROR \t-  \'site_name\' not found in file \'%s\'. Please, check the configuration written in the file.' % ( repo_path+subsite_path+"mkdocs.yml" )
      return

    subsites[subsite_name] = subsite_path

  extra_conf = {}
  extra_conf["subsites"] = subsites

  landing_extra_conf = {}
  landing_extra_conf["subsites"] = subsites
  landing_extra_conf["landing_page"]='True'


  # Once we know the name of all subsites, we can start building them, starting with the landing page
  landing_page_compiler_output = compile_single(repo_path, landing_extra_conf, compiled_site_root_folder)

  compiler_output = {}
  for subsite_name in subsites:
    site_name = subsite_name.replace(" ", "_").lower()

    # Delete the site compiled folder if it already exists
    if output_folder is None and path.exists(compiled_site_root_folder+site_name):
      sh.rm("-r", compiled_site_root_folder+site_name)

    if subsites[subsite_name] == './':
      source_folder = repo_path
    else:
      source_folder = repo_path+subsites[subsite_name]

    print "INFO \t-  Calling compiling for subsite \'%s\'" % ( source_folder )

    compiled_subsite_root_folder = compiled_site_root_folder+subsites[subsite_name].split("/")[-2]
    compiler_output[subsite_name] = compile_single(source_folder, extra_conf, compiled_subsite_root_folder)


  # Fix links between subsite pages
  missing_link_regex = re.compile("WARNING -  The page \"(?P<page>.+?)\" contained a hyperlink to \"(?P<link>.+?)\" which is not listed in the \"pages\" configuration.*$")
  for subsite_name in compiler_output:
    print "\nINFO \t-  Showing output for '%s' subsite compilation" % subsite_name
    links_to_replace = {}

    # Compile the broken links for every subsite page
    for compiler_output_line in clean_duplicate_lines( compiler_output[subsite_name].split('\n') ):

      if compiler_output_line == 'WARNING -  Config value: \'subsites\'. Warning: Unrecognised configuration name: subsites ':
        continue

      missing_links = missing_link_regex.match(compiler_output_line)

      if missing_links:
        if missing_links.group("page") not in links_to_replace:
          links_to_replace[missing_links.group("page")]=[]

        links_to_replace[missing_links.group("page")].append(missing_links.group("link"))
      
        # Print only the warnings to files that don't apear on the compiled site
        if missing_links.group("page") == "index.md":
          compiled_subsite_page_path = compiled_site_root_folder+subsites[subsite_name].split("/")[-2]+"/index.html"
        else:
          compiled_subsite_page_path = compiled_site_root_folder+subsites[subsite_name].split("/")[-2]+"/"+missing_links.group("page").split(".md")[0]+"/index.html"

        compiled_subsite_root_folder = compiled_site_root_folder+subsites[subsite_name].split("/")[-2]

        if not compiled_file_exists ( compiled_subsite_root_folder, missing_links.group("page"), missing_links.group("link") ):
          print compiler_output_line
      else:
        if compiler_output_line != "": print compiler_output_line

    compiled_subsite_root_folder = compiled_site_root_folder+subsites[subsite_name].split("/")[-2]

    # Use links_to_replace to replace the link to the md and change it to a link to the compiled site
    replace_broken_links( compiled_subsite_root_folder, subsite_name, subsites, links_to_replace )

  print "INFO \t-  End of multisite compilation\n"
#end compile-multi_command

def config_command( value=None, config_variable=None ):
  """ Commmand to allow to read/write configuration variables. 
  If value argument is None, the commmand will show the configuration variables. If value contains something, then then script will update wih its content the variable specified in config_variable. """
  
  global default_theme_folder

  if value is None:
    print "Not editable variables:"
    print "\t - conf_folder: ", conf_folder
    print "\t - build_folder: ", build_folder
    print "Editable variables:"
    print "\t - default_theme_folder: ", default_theme_folder
  else:

    if config_variable != 'default_theme_folder':
      print "The config variable specified will not be used. Current editable config variables are: "
      print "\t- 'default_theme_folder'"
      return
    else:
      conf={}
      conf['default_theme_folder']=value
      default_theme_folder = value

    with open(conf_folder+"mkdocs-builder.yml", "w") as outfile:
      outfile.write( yaml.dump(conf, default_flow_style=False) )
#end config_command

def setup_script():
  """ Utility to init the configuration variables """

  script_filename = inspect.getframeinfo(inspect.currentframe()).filename
  script_folder = normalise_folder_paths( os.path.dirname(os.path.abspath(script_filename)) )

  conf_folder = normalise_folder_paths( path.abspath ( path.expanduser(script_folder+'conf/') ) )
  sh.mkdir("-p", conf_folder)

  build_folder = normalise_folder_paths( path.abspath ( path.expanduser(script_folder+'.tmp_build/') ) )
  sh.mkdir("-p", build_folder)

  conf = {}
  if not path.isfile(conf_folder+"/mkdocs-builder.yml"):
    conf['default_theme_folder'] = normalise_folder_paths( path.abspath( path.expanduser( script_folder+'./custom_theme') ) )

    with open(conf_folder+"mkdocs-builder.yml", "w") as outfile:
      outfile.write( yaml.dump(conf, default_flow_style=False) )

  else:
    with open(conf_folder+"mkdocs-builder.yml", "r") as infile:
      conf = yaml.load(infile)

  return conf_folder, build_folder, conf['default_theme_folder']
#def setup_script

if __name__ == '__main__':
  import scriptine
  import os.path as path
  import os
  import sh
  import yaml
  import subprocess
  import datetime
  import re
  import pprint
  import inspect
  import shutil
  import errno

  conf_folder, build_folder, default_theme_folder = setup_script()

  scriptine.run()

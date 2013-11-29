---
layout: post.html
title: 'running with mynt'
tagline: 'static site generation as a blogging platform'
---

#Low pressure, high performance blogging

I've been in the market for a solid blogging platform for some time. I've built fully featured blog engines with [django](http://djangoproject.com), played with drop-in solutions like [wordpress](http://wordpress.com) and [drupal](http://drupal.com), as well as trying hosted solutions like [tumblr](http://tumblr.com). It always ended the same; I found myself spending more time worrying about the platform than actually writing. I would have to spend a non-trivial amount of time and effort becoming familiar with the domain specific idiosyncrasies of each product, what was required to theme the project, extend functionality, or more often than not, what was required to purge unnecessary features. All the platforms I mentioned are rich, mature and suitable blogging platforms.  They also aren't what I have been looking for. 

Yesterday I read about a new static site generator on the [Planet Python](http://planet.python.org) feed, called [mynt](http://mynt.mirroredwhite.com) written by [Andrew Fricke](http://mirroredwhite.com). It boasted a rich feature-set and simplicity. It was written in python and used markdown and jinja2 for layout and content. I was familiar with the tools so I decided to give it a go.  

##Setting up the project

###Installation
Installation was a breeze, I created a new isolated python environment with 
`mkvirtualenv samelog -p /usr/bin/python2.7` (mynt needs python 2.7 since it uses some core libraries like argparse not found in earlier versions of 2.x -- oh, and you're using Doug Hellmann's [virtualenvwrapper](http://www.doughellmann.com/projects/virtualenvwrapper/) already, aren't you?). I then installed with a simple `pip install mynt`, made sure that `mynt --version` returned a sane response to check the install and I was ready for the races.

###Creating our project
Unfortunately mynt doesn't come with any scripts to generate a dummy project, but I found the source to Andrew's personal site helpful as a starting point. Luckily, you can find this up on [github](https://github.com/Anomareh/MirroredWhite).  In either case, you should be set by simply running this command in your project directory:

~~~~{sh}
mkdir _assets _templates _posts && \
mkdir _assets/css && \
touch index.html config.yml \
_posts/2012-12-21-doomsday.md _assets/css/screen.css \
_templates/base.html _templates/post.html
~~~~

This will create all the necessary files for your project, of course you'll need to fill in the content yourself.

###Configuration
Mynt uses [yaml](http://yaml.org/) for configuration in both templates and project config.  An exhaustive list of config options can be found at mynts documentation. However, I just needed one:

~~~~{yaml}
base_url: log/
~~~~

This tells mynt that it's mounted at /log/ rather than / and to handle assets/urls accordingly, simple enough!

###Building out your minimum viable blog
Fist things first, we'll need a layout.  Open up `_templates/base.html` in your favorite text editor and give it something like this:

~~~~{jinja}
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='utf-8'>
    <title>{{ '{% block title %}' }}My Blog{{ '{% endblock %}' }}</title>
    <link rel='stylesheet' href='{{ '{{ get_asset("css/screen.css") }}' }}'>
</head>
<body>
    <section class='content'>
    {{ '{% block content %}Welcome to my blog.{% endblock %}' }}
    </section>
</body>
</html>
~~~~

Hopefully this is simple enough for you, if you've used twig in php, django, or jinja templates before.  We're just setting up two blocks to be replaced by other templates, accessible via `block title` and `block content`.  The `get_asset()` bit is specific to mynt, it returns the uri path relative to your mynt project and the `_assets/` folder we created earlier.

Next, let's create our template for posts themselves.  Posts can have any amount of variables thrown into them by yaml frontmatter.  In our example however, we'll reference only the `posts` variable provided by mynt.

`_templates/post.html`

~~~~{jinja}
{% raw %}{% extends "base.html" %}
{% block title %}{{ block.super }} - {{ post.title }}{% endblock %}
{% block content %}
<article>
    <header>
        <h1>{{ post.title }}</h1>
        <small>{{ post.date }}</small>
    </header>
    <section>
        {{ post.content }}
    </section>
</article>
{% endblock %}{% endraw %}
~~~~

This will set the title of our base template to 'My Blog - My Post Title' and fill the content section up with the data of the post itself.  

Finally, we just need a simple way to view a list of the posts.  We'll do this by editing `index.html`.  As a quick caveat, any html or xml file not located in _assets, _templates, or _posts, and not beginning with a . or _ will be treated as a standard jinja2 template, with folder structure preserved and access to the global variables `site`, `posts`, `archives`, and `tags`. (Yes, that means that your project/rss/rss.xml file can be a jinja2 template and available at /rss/rss.xml). Visit the mynt documentation for more information. We'll leverage this right now when creating our post listing.

`index.html`

~~~~{jinja}
{% raw %}{% extends "base.html" %}
{% block content %}
<h1>Welcome to my blog, please, check out some of my posts!</h1>
<ul>
    {% for post in posts %}
        <li>
            <a href='{{ get_url(post.url) }}'>{{ post.title }}</a>
            <small>{{ post.date }}</small>
        </li>
    {% endfor %}
</ul>
{% endblock %}{% endraw %}
~~~~

Nothing new here, save the use of a for loop to iterate over the posts object, and the `get_url()` builtin to generate the url string for a given post.  But that's all we need.  With these 3 small templates, we are ready to start creating our content.

###Creating content nodes

Content in mynt is written in markdown by default.  Every piece of content must be located in the posts folder, begin with a YYYY-MM-DD date string, and the contents of the file must contain yaml frontmatter referencing the layout and the title of the post.

~~~~{markdown}
---
layout: post.html
title: 'My first post'
---

##I made it ma, i'm blogging!

Lorem ipsum here
~~~~

The post might not be all that shiny, but it's the layout that matters. The three dashes delimit the yaml config for the post which in turn become variables accessible to your templates. (remember how we used post.title earlier? this is where it comes from!).  Everything below gets parsed as markdown, with access to the special markdown fences for code blocks. (example of that [here](https://gist.github.com/1687005))

That's it! Run `mynt _deploy` from your project root and your static blog will be generated! Easy, huh?

###Automating tasks with fabric
However, we can do better.  When working with a static site generator, there are often a lot of tasks you need to repeat; generating the content, moving it to its proper deploy environment, or cleaning up the generated files. Luckily, [fabric](http://docs.fabfile.org/) makes repeated tasks like these simple.

Let's look at the fabfile all at once, and then we'll drill down into the specifics of what each part does.

~~~~{python}

from fabric.api import local
import fabric.contrib.project as project

ROOTDIR = '/home/egghead/www/samelog'
MYNT_PATH = '/home/egghead/.virtualenvs/samelog/bin/mynt'
PROJECT_NAME = 'samelog'

def clean():
    local('rm -rf %s/_deploy' % ROOTDIR)

def generate():
    local('%s %s/_deploy' % (MYNT_PATH, ROOTDIR))

def deploy():
    local('scp -r %s/_deploy/* daat:www/samelog' % ROOTDIR)

def regen():
    clean()
    generate()

def redeploy():
    regen()
    deploy()
    clean()
~~~~

Fabric itself is a bit of an ssh toolkit for python, letting you run arbitrary operations across numerous machines.  However, since we're just working locally, we'll only import 'local'.  We'll import a fabric project to set things up, and declare a few variables to make the script easier to change down the line.  Each function defined in a fabfile is available via the command `fab function`, so we could run `fab clean` to remove the _deploy directory, `fab generate` to generate the static blog, or build functions out of the combinations of these.  The one I find myself running the most is `fab redeploy` to clean up the current deploy folder, regenerate the content, and push it over the wire to the folder that's exposed to the web.  (In my case I'm using scp, yours could very well be a cp).  Finally after deploying we clean up the files we generated.  Less typing, more time for other things!

## Wrapping up

All things considered, I'm enthralled by the simplicity and flexibility mynt offers.  I was able to get it up and running in a day with minimal effort, and am bubbling with ideas about how to take advantage of the simple key/value store provided by the yaml frontmatter; accessible via the jinja2 templates.  I had tried alternatives like [hyde](http://ringce.com/hyde) before but always wound up getting lost in the complexity, jumping down one of the rabbit holes in its feature-set and realizing hours later that I've yet to produce anything productive.  mynt's power on the other hand lies in its simplicity.  It's just python under the hood, but what you can do with jinja2/yaml/markdown alone is immense.  The focus is exposed simplicity, not hiding waiting to be found.  (That said I've yet to peek too deeply under the hood of mynt... but I'll leave that for another day!).

In any case, I hope you try [mynt](http://mynt.mirroredwhite.com/docs/) out for yourself and let me know what you think!

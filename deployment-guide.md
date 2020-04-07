# Deployment guide
## Technology stack
* Python
* Flask: python framework
* PostgreSql: database to store the tokens to communicate with any workspace that installed the bot
* Heroku: cloud hosting
* Git
* virtualenv


## To create your slack app follow this link
https://api.slack.com/bot-users

## Public Distribution of the app

### Add the slack bot to any slack workspace
Go to this link to add it
https://botcryptoslack.herokuapp.com/begin_auth

<a href="https://slack.com/oauth/v2/authorize?client_id=1034315777795.1044752003316&scope=chat:write,channels:join,commands,im:history,im:write,app_mentions:read,channels:history"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"></a>
### Include this html link in any website
    <a href="https://slack.com/oauth/v2/authorize?client_id=1034315777795.1044752003316&scope=chat:write,channels:join,commands,im:history,im:write,app_mentions:read,channels:history"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"></a>

## Deploy bot on heroku infrastructure

create your own project or clone/fork this repo

Install the Heroku CLI used to deploy to heroku

You can create yor heroku app and pipeline in https://heroku.com. If you want to create your heroku app using the cli-command follow this link https://devcenter.heroku.com/articles/git.

### PostgreSql database
The database is used to store the tokens provided by slack of the workspaces that installed the bot. These tokens are used to communicate with the corresponding workspace.
To install postgreSql free plan in heroku you need to run this command

    heroku addons:create heroku-postgresql:hobby-dev 


Assuming you have an existing git repository(because you forked or cloned this repo or creted you own)
To link your heroku app with your local git repo use this command

    heroku git:remote -a [heroku_app]
Be sure to change [heroku_app] with the name of your heroku app.

### Deploying cli-command
git push heroku master
This command will deploy to heroku the project. For python heroku use the requirements.txt to install needed dependencies. So in case you install new python 
dependencies run pip freeze > requirements.txt to update it with your latest dependencies.

Once this is done there is one more step to follow if you forked/cloned this repo. Create the database in postgreSql in heroku with this command.

    heroku run python manage.py upgrade

### Important
In the case you created your own project and database you should probably need to initialize database and run migrations. Migrations folder needs to be in your repo and uploaded to git because you will need it to tell heroku to generate your database.

    heroku run python manage.py init
    heroku run pyton manage.py migrate



### In case you have any problem run in your cli

    heroku logs -t

to see the latest logs of your heroku instance.

If everything was ok and you configured you bot as public now you can add the bot to any workspace using the provided links.



## Useful links
*  heroku
1. https://heroku.com
2. https://devcenter.heroku.com/articles/git
3. https://elements.heroku.com/addons/heroku-postgresql
4. https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/

*  Flask, python app, heroku
1. https://stackabuse.com/deploying-a-flask-application-to-heroku/
2. https://medium.com/the-andela-way/deploying-a-python-flask-app-to-heroku-41250bda27d0

*  Slack
1. https://api.slack.com/bot-users
2. https://api.slack.com/methods/oauth.v2.access
3. https://api.slack.com/events-api#receiving_events




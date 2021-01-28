# GuelphScheduler2

https://beta.aceparent.me/#/scheduler


Create schedules for the university of Guelph. Live version can be found [here](https://guelph.scheduler.online "Guelph Course Scheduler")

### Prerequisites
The following dependencies must be installed:

- npm
- nodejs
- mongodb
- mongodb c++ drivers [https://github.com/mongodb/mongo-cxx-driver](https://github.com/mongodb/mongo-cxx-driver)


### Installing

Compile the c++ scheduling program

```
cd searchAlgorithm && make
```

Install nodejs dependencies

```
cd webserver && npm install
```

## Deployment

Run `python3 webserver/schools/Guelph/getClasses.py` to populate the course database. This will take a few minutes to complete.

Run `npm run start` to start the project. This will by default start the server on port 3000. This can be configued in `app.js`

## Built With

* [Bootstrap](https://getbootstrap.com/docs/4.1/getting-started/introduction/) - The web framework
* [Mongodb](https://www.mongodb.com/) - Database
* [Fullcalendar](https://fullcalendar.io/) - Integrated calendar

## Authors

* **Alexander Parent** - *Initial work* - [iam4722202468](https://github.com/iam4722202468)

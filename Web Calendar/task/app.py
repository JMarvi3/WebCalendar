import datetime
from flask import Flask
from flask_restful import Resource, Api, reqparse, inputs, marshal, fields
from flask_sqlalchemy import SQLAlchemy
import sys


class DateFormat(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')


event_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': DateFormat
}


class EventResource(Resource):
    def get(self):
        args = date_parser.parse_args()
        events = Event.query
        if args['start_time'] and args['end_time']:
            events = events.filter(Event.date >= args['start_time'].date(), Event.date <= args['end_time'].date())
        return marshal(events.all(), event_fields)

    def post(self):
        args = parser.parse_args()
        db.session.add(Event(**args))
        db.session.commit()
        date_str = args['date'].strftime("%Y-%m-%d")
        return {'message': 'The event has been added!', 'event': args['event'], 'date': date_str}


class EventTodayResoruce(Resource):
    def get(self):
        events = Event.query.filter_by(date=datetime.date.today()).all()
        if not events:
            return {"data": "There are no events for today!"}, 400
        return marshal(events, event_fields)


class EventById(Resource):
    def get(self, id):
        event = Event.query.filter_by(id=id).first()
        if event is None:
            return {'message': "The event doesn't exist!"}, 404
        return marshal(event, event_fields)

    def delete(self, id):
        event = Event.query.filter_by(id=id).first()
        if event is None:
            return {'message': "The event doesn't exist!"}, 404
        db.session.delete(event)
        db.session.commit()
        return {'message': 'The event has been deleted!'}


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///event.db'
api = Api(app)
db = SQLAlchemy(app)
db.init_app(app)
app.app_context().push()


class Event(db.Model):
    __table_name__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)


api.add_resource(EventResource, '/event')
api.add_resource(EventById, '/event/<int:id>')
api.add_resource(EventTodayResoruce, '/event/today')

parser = reqparse.RequestParser()
parser.add_argument('event', type=str, help='The event name is required!', required=True)
parser.add_argument('date', type=inputs.date,
                    help='The event date with the correct format is required! The correct format is YYYY-MM-DD!',
                    required=True)

date_parser = reqparse.RequestParser()
date_parser.add_argument('start_time', type=inputs.date, help='The start date in the format YYYY-MM-DD')
date_parser.add_argument('end_time', type=inputs.date, help='The start date in the format YYYY-MM-DD')

# do not change the way you run the program
if __name__ == '__main__':
    db.create_all()
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()

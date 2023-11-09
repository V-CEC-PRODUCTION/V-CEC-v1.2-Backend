import pusher

pusher_client = pusher.Pusher(
  app_id='1700959',
  key='bd8c40cd91154940fd47',
  secret='fe4141e4a50de0f4ad0f',
  cluster='ap2',
  ssl=True
)

pusher_client.trigger('my-channel', 'my-event', {'message': 'hello world'})
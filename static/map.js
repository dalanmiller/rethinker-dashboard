

ContribMap = Ember.Application.create();

ContribMap.Router.map(function(){
  this.resource('map', { path: '/' });
  this.resource('users');
  this.resource("user", { path: ":user_id"})
});

ContribMap.MapController = Ember.Controller.extend({
  latitude: 0,
  longitude: 0,
  zoom: 1
});

ContribMap.Users = DS.Model.extend({
  login: DS.attr('string'),
  coords: DS.attr('string'),
});

// App.PostAdapter = DS.RESTAdapter.extend({
//   namespace: 'api/v1'
// });

ContribMap.UserAdapter = DS.RESTAdapter.extend({
  namespace: "api"
})

ContribMap.UsersAdapter = DS.RESTAdapter.extend({
  namespace: "api"
})


ContribMap.UsersRoute = Ember.Route.extend({
  model: function() {
    return this.store.find('users');
  }
});

ContribMap.UserRoute = Ember.Route.extend({
  model: function(params){
    return this.store.find("users", params.post_id);
  }
})

ContribMap.MapRoute = Ember.Route.extend({
  model: function(){
    return this.store.findAll("users");
  },
  setupController: function() {
    console.log("INDEXROUTE SETUPCONTROLLER");
    // var users = ContribMap.User.find();
    var users = [];
    this.controllerFor('map').set('users', users);
  }
});

ContribMap.LeafletMapComponent = Ember.Component.extend({
  attributeBindings: ['style'],

  width: 'auto',
  height: '600px',
  latitude: 0,
  longitude: 0,
  zoom: 1,

  style: function() {
    console.log("STYLE");
    console.log(this);
    return [
      'width:' + this.get('width'),
      'height:' + this.get('height')
    ].join(';');
  }.property('width', 'height'),

  setView: function() {
    var map    = this.get('map'),
  			center = [this.get('latitude'), this.get('longitude')],
				zoom   = this.get('zoom');

		map.setView(center, zoom);
  }.observes('latitude', 'longitude', 'zoom'),

  didInsertElement: function() {
    var map = L.map(this.get('element'));

    var users = this.get("users");

    console.log("users");
    console.log(users);

    console.log(this.model);

    this.set('map', map);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom: 18,
      id: 'dalanmiller.008a9358',
      accessToken: "pk.eyJ1IjoiZGFsYW5taWxsZXIiLCJhIjoiZDg0MWY0MjMzZjE4Y2VkOGE4NGY1ZTI5ZTg5MjUzMTMifQ.ylhul8dwba3XpBQDOkTK6w"
    }).addTo(map);

    this.setView();

    map.on('move', this.mapDidMove, this);

    map.invalidateSize();
  },

  // willRemoveElement: function() {
  //   var map = this.get('map');
  //   if (map) map.remove();
  // },
  //
  mapDidMove: function() {
    var map    = this.get('map'),
        center = map.getCenter(),
        zoom   = map.getZoom();

    this.setProperties({
      latitude: center.lat,
      longitude: center.lng,
      zoom: zoom
    });
  }
});

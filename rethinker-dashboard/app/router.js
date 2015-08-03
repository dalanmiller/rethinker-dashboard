import Ember from 'ember';
import config from './config/environment';

var Router = Ember.Router.extend({
  location: config.locationType
});

Router.map(function() {
  this.resource("user", { path: "/user/:user_id" });
  this.resource("map", { paht: "/map"});
});

export default Router;

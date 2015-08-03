import DS from 'ember-data';

export default DS.Model.extend({
    login: DS.attr('string'),
    location: DS.attr("string")
});

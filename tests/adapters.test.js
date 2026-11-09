import test from 'node:test';
import assert from 'node:assert/strict';
import { selectZones, addLeafletZones, addGoogleZones } from '../src/index.js';

const feature=(id,status,country='DE')=>({type:'Feature',id,properties:{id,name:id,status,country},geometry:{type:'MultiPolygon',coordinates:[[[[10,50],[11,50],[11,51],[10,50]]],[[[12,50],[13,50],[13,51],[12,50]]]]}});
const data={type:'FeatureCollection',features:[feature('a','active'),feature('b','abolished'),feature('c','active','FR')]};

test('active is default; country and all filters work without mutating input',()=>{
  const before=JSON.stringify(data);
  assert.deepEqual(selectZones(data).features.map(f=>f.id),['a','c']);
  assert.deepEqual(selectZones(data,{country:'DE',status:'all'}).features.map(f=>f.id),['a','b']);
  assert.equal(selectZones(data,{country:'XX'}).features.length,0);
  assert.equal(JSON.stringify(data),before);
  assert.throws(()=>selectZones({type:'Polygon'}),TypeError);
});

test('Leaflet receives unmodified GeoJSON order and skips fitting empty results',()=>{
  let received,fit=0;
  const map={fitBounds(){fit++;}};
  const L={geoJSON(collection){received=collection;return {addTo(){return this;},getBounds(){return {isValid:()=>collection.features.length>0};}};}};
  addLeafletZones(L,map,data,{country:'DE'});
  assert.deepEqual(received.features[0].geometry.coordinates[0][0][0],[10,50]);
  assert.equal(fit,1);
  addLeafletZones(L,map,data,{country:'XX'});
  assert.equal(fit,1);
});

test('Google adapter creates an independent Data layer and fits every component',()=>{
  let fitted,layerMap;
  class Data {
    constructor({map}){layerMap=map;}
    addGeoJson(collection){this.collection=collection;return collection.features.map(f=>({getGeometry:()=>({forEachLatLng(callback){for(const poly of f.geometry.coordinates)for(const ring of poly)for(const coord of ring)callback(coord);}})}));}
    setStyle(fn){this.style=fn;}
    addListener(){}
  }
  class LatLngBounds {constructor(){this.points=[];}extend(p){this.points.push(p);}isEmpty(){return !this.points.length;}}
  const google={maps:{Data,LatLngBounds,InfoWindow:class{}}};
  const map={fitBounds(bounds){fitted=bounds;}};
  const layer=addGoogleZones(google,map,data,{country:'DE'});
  assert.equal(layerMap,map);
  assert.deepEqual(layer.collection.features.map(f=>f.id),['a']);
  assert.equal(fitted.points.length,8);
  assert.deepEqual(fitted.points[4],[12,50]);
  assert.equal(layer.style({getProperty:()=> 'abolished'}).strokeColor,'#707984');
});

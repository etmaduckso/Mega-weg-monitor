db = db.getSiblingDB('admin');
db.system.version.updateOne(
  { "_id": "featureCompatibilityVersion" },
  { "$set": { "version": "6.0" } },
  { "upsert": true }
);

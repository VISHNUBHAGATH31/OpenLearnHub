const { MongoClient } = require('mongodb');

async function updateDocuments() {
  const client = new MongoClient('mongodb://localhost:27017/Documents?retryWrites=true&w=majority', { useNewUrlParser: true, useUnifiedTopology: true });

  try {
    await client.connect();
    const database = client.db('Documents');
    const collection = database.collection('storage');

    await collection.updateMany(
        { "chapter": { $exists: true, $type: 16 } }, // Update "chapter" from int to string
        [
          { $set: { "chapter": { $toString: "$chapter" } } }
        ]
      );
  
      console.log('Update successful for "chapter" attribute');
  } finally {
    await client.close();
  }
}

updateDocuments();

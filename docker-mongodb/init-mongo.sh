#!/bin/bash
set -e

echo "Starting MongoDB initialization..."
sleep 2

# Create user using local connection (no port specification needed)
echo "Creating user..."
mongosh --eval "
const adminDb = db.getSiblingDB('admin');
try {
   adminDb.createUser({
      user: 'mongotUser',
      pwd: 'mongotPassword',
      roles: [{ role: 'searchCoordinator', db: 'admin' }]
   });
   print('User mongotUser created successfully');
} catch (error) {
   if (error.code === 11000) {
      print('User mongotUser already exists');
   } else {
      print('Error creating user: ' + error);
   }
}
"

# Check for existing data
echo "Checking for existing sample data..."
# (Simplified check or omitted if searching on existing collections)

echo "MongoDB initialization completed."

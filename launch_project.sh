# Delete the docker compose images
cd docker
docker compose down
echo "Shutting down docker compose images. Done."

# Make analyzer again
echo -n "Make: analyzer. "
cd analyzer
make > /dev/null 2>&1
echo "Done."

# Make dashboard again
echo -n "Make: dashboard. "
cd ../dashboard
make > /dev/null 2>&1
echo "Done."

# Docker compose up
cd ..
docker compose up

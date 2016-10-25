set -e

export HOST=localhost

echo "Creating a token to run benchmarks with..."
ADMIN_TOKEN=`python authenticate.py`
SUBJECT_TOKEN=`python authenticate.py`
echo "Admin token: $ADMIN_TOKEN"
echo "Subject token: $SUBJECT_TOKEN"

echo "Warming up Apache..."
ab -c 100 -n 1000 -T 'application/json' http://$HOST:35357/ > /dev/null 2>&1

echo "Benchmarking token creation..."
ab -r -c 1 -n 200 -p auth.json -T 'application/json' http://$HOST:35357/v3/auth/tokens

echo "Benchmarking token validation..."
ab -r -c 1 -n 1000 -T 'application/json' -H "X-Auth-Token: $ADMIN_TOKEN" -H "X-Subject-Token: $SUBJECT_TOKEN" http://$HOST:35357/v3/auth/tokens

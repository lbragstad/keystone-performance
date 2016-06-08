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
ab -r -c 1 -n 200 -p auth.json -T 'application/json' http://$HOST:35357/v3/auth/tokens > create_token
if ! grep -q 'Failed requests:        0' create_token; then
  echo 'WARNING: Failed requests!'
fi
git diff --color create_token | grep --fixed-strings ' [ms] (mean)' || true

echo "Benchmarking token validation..."
ab -r -c 1 -n 10000 -T 'application/json' -H "X-Auth-Token: $ADMIN_TOKEN\n" -H "X-Subject-Token: $SUBJECT_TOKEN\n" http://$HOST:35357/v3/auth/tokens > validate_token
if ! grep -q 'Failed requests:        0' validate_token; then
  echo 'WARNING: Failed requests!'
fi
git diff --color validate_token | grep --fixed-strings ' [ms] (mean)' || true

echo "Benchmarking token creation concurrently..."
ab -r -c 100 -n 2000 -p auth.json -T 'application/json' http://$HOST:35357/v3/auth/tokens > create_token_concurrent
if ! grep -q 'Failed requests:        0' create_token_concurrent; then
  echo 'WARNING: Failed requests!'
fi
git diff --color create_token_concurrent | grep --fixed-strings ' [#/sec] (mean)' || true

echo "Benchmarking token validation concurrency..."
ab -r -c 100 -n 100000 -T 'application/json' -H "X-Auth-Token: $ADMIN_TOKEN" -H "X-Subject-Token: $SUBJECT_TOKEN" http://$HOST:35357/v3/auth/tokens > validate_token_concurrent
if ! grep -q 'Failed requests:        0' validate_token_concurrent; then
  echo 'WARNING: Failed requests!'
fi
git diff --color validate_token_concurrent | grep --fixed-strings ' [#/sec] (mean)' || true
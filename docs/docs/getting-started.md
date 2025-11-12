Getting started
===============

# Environment installs
To activate this environment, use:

    mamba activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh

    source activate /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh


# Environment updates
mamba env update --prefix /scratch/cs/ecanet/polwell-mental-health/polwell_mh/envs/polwell_mh --file environment.yml --prune




pytest -v tests/test_query_user_posts_and_comments.py  --input /m/cs/scratch/sinitaivas/bluesky_firehose/firehose_stream/2024-12-17/2024-12-17T21.ndjson.gz   --script /scratch/cs/ecanet/polwell-mental-health/polwell_mh/polwell_mh/preprocess/query_users_posts.py   --output /tmp/test_user_posts.parquet   --n_users 5
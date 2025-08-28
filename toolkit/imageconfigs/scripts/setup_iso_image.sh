#!/bin/bash
# Copyright (c) Intel Corporation.
# Licensed under the MIT License.

set -e

ls /usr/lib
ls /etc/image-id
cat /etc/image-id
cp /etc/image-id /usr/lib/image-id
ls ../
ls ../../

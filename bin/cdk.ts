#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib'
import { PypiStack } from '../lib/pypi-stack'

const app = new cdk.App()
new PypiStack(app, 'PypiNotifierStack', {

  env: { account: '821523470585', region: 'us-east-1' },

  /* For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html */
})
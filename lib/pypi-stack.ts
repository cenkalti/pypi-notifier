import * as cdk from 'aws-cdk-lib'
import { Construct } from 'constructs'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as lambdaPython from '@aws-cdk/aws-lambda-python-alpha'

export class PypiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    new lambdaPython.PythonFunction(this, 'Function', {
      runtime: lambda.Runtime.PYTHON_3_8, // required
      entry: 'pypi_notifier', // required
      index: 'hello.py', // optional, defaults to 'index.py'
      handler: 'handler', // optional, defaults to 'handler'
    })
  }
}

# Amazon Bedrock Configuration Fix Guide

## Problem Description

You encountered this error when using Cline with Amazon Bedrock:

```
[ERROR] Failed to process response: Invocation of model ID anthropic.claude-sonnet-4-20250514-v1:0 with on-demand throughput isn't supported. Retry your request with the ID or ARN of an inference profile that contains this model.
```

This error occurs because the specific model ID `anthropic.claude-sonnet-4-20250514-v1:0` doesn't support on-demand throughput and requires an inference profile configuration instead.

## Solution Options

### Option 1: Use a Supported Model ID (Recommended)

The quickest fix is to change your Cline configuration to use a model that supports on-demand throughput.

#### Steps:
1. **Open Cline Settings**
   - Click the gear icon in the Cline interface
   - Navigate to the model configuration section

2. **Update Model ID**
   Replace the current model ID with one of these supported alternatives:

   **Recommended Models:**
   ```
   anthropic.claude-3-sonnet-20240229-v1:0    # Similar capabilities to what you were using
   anthropic.claude-3-haiku-20240307-v1:0     # Faster and more cost-effective
   anthropic.claude-3-opus-20240229-v1:0      # Most capable (higher cost)
   ```

3. **Save Configuration**
   - Save the settings
   - Restart Cline if necessary

### Option 2: Create and Use an Inference Profile

If you specifically need to use the `anthropic.claude-sonnet-4-20250514-v1:0` model:

#### Steps:
1. **Access AWS Bedrock Console**
   - Log into your AWS account
   - Navigate to Amazon Bedrock service

2. **Create Inference Profile**
   - Go to "Inference profiles" in the left sidebar
   - Click "Create inference profile"
   - Add the Claude Sonnet model to the profile
   - Configure throughput settings

3. **Get Profile ARN**
   - Copy the inference profile ARN (format: `arn:aws:bedrock:region:account:inference-profile/profile-name`)

4. **Update Cline Configuration**
   - Use the inference profile ARN instead of the model ID
   - Format: Use the full ARN in place of the model ID

### Option 3: Set Up Provisioned Throughput

For consistent performance and the specific model:

#### Steps:
1. **Purchase Provisioned Throughput**
   - In AWS Bedrock console, go to "Provisioned throughput"
   - Purchase throughput for your desired model
   - Note the provisioned model ARN

2. **Update Configuration**
   - Use the provisioned model ARN in Cline settings

## Model Comparison

| Model | Speed | Cost | Capabilities | Best For |
|-------|-------|------|--------------|----------|
| Claude 3 Haiku | Fast | Low | Good | Quick tasks, coding assistance |
| Claude 3 Sonnet | Medium | Medium | Very Good | Balanced performance |
| Claude 3 Opus | Slower | High | Excellent | Complex reasoning, analysis |

## Troubleshooting

### Common Issues:

1. **"Model not found" error**
   - Verify the model ID is correct
   - Check if the model is available in your AWS region
   - Ensure you have proper permissions

2. **Authentication errors**
   - Verify AWS credentials are properly configured
   - Check IAM permissions for Bedrock access

3. **Region availability**
   - Some models may not be available in all regions
   - Check AWS Bedrock documentation for model availability

### Testing Your Configuration:

After making changes:
1. Save your Cline settings
2. Try a simple test command
3. Verify no Bedrock errors appear
4. Test with a more complex task to ensure full functionality

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude Models Guide](https://docs.anthropic.com/claude/docs)
- [Cline Configuration Documentation](https://docs.cline.bot/)

## Quick Reference

**Most Common Fix:**
Replace your model ID with: `anthropic.claude-3-sonnet-20240229-v1:0`

**Emergency Fallback:**
Use: `anthropic.claude-3-haiku-20240307-v1:0` for fastest resolution

---

*Last updated: January 2025*

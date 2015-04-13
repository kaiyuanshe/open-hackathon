require 'rest-client'
require 'time'
require 'openssl'
require 'base64'

class Citadel
  module S3
    extend self

    # Global state, boo
    RestClient.proxy = ENV['http_proxy']

    def get(bucket, path, aws_access_key_id, aws_secret_access_key, token=nil)
      path = "/#{path}" unless path[0] == '/'
      now = Time.now().utc.strftime('%a, %d %b %Y %H:%M:%S GMT')

      string_to_sign = "GET\n\n\n#{now}\n"
      string_to_sign << "x-amz-security-token:#{token}\n" if token
      string_to_sign << "/#{bucket}#{path}"

      signed = OpenSSL::HMAC.digest(OpenSSL::Digest::Digest.new('sha1'), aws_secret_access_key, string_to_sign)
      signed_base64 = Base64.encode64(signed)

      headers = {
        date: now,
        authorization: "AWS #{aws_access_key_id}:#{signed_base64}",
      }
      headers['x-amz-security-token'] = token if token
      RestClient::Request.execute(method: :get, url: "https://s3.amazonaws.com/#{bucket}#{path}", raw_response: true, headers: headers)
    end

  end
end

class Citadel
  def initialize(node, bucket)
    @node = node
    @bucket = bucket
  end

  def [](key)
    self.class.get(@node, @bucket, key)
  end

  def self.get(node, bucket, key)
    bucket ||= node['citadel']['bucket']
    if node['citadel']['access_key_id']
      # Manually specified credentials
      key_id = node['citadel']['access_key_id']
      secret_key = node['citadel']['secret_access_key']
      token = nil
    elsif node['ec2'] && node['ec2']['iam'] && node['ec2']['iam']['security-credentials']
      # Creds loaded from EC2 metadata server
      # This doesn't yet handle expiration, but it should
      role_creds = node['ec2']['iam']['security-credentials'].values.first
      key_id = role_creds['AccessKeyId']
      secret_key = role_creds['SecretAccessKey']
      token = role_creds['Token']
    else
      raise 'Unable to load secrets from S3, no S3 credentials found'
    end
    puts("citadel: Retrieving #{bucket}/#{key}")
    Citadel::S3.get(bucket, key, key_id, secret_key, token)
  end

  # Helper module for the DSL extension
  module ChefDSL
    def citadel(bucket=nil)
      Citadel.new(node, bucket)
    end
  end
end


node = {
  'citadel' => {
    'bucket' => 'balanced.citadel',
    'access_key_id' => ENV['BALANCED_AWS_ACCESS_KEY_ID'],
    'secret_access_key' => ENV['BALANCED_AWS_SECRET_ACCESS_KEY'],
  }
}

s = Citadel.new(node, nil)
puts s['deploy_key/deploy.pem']

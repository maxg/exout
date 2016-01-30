#!/usr/bin/ruby

require 'cgi'
require 'openssl'
require 'yaml'

CONF = YAML.load_file('config/course-setup.yaml')
KEY = IO.read('config/key.txt')

SHA1 = OpenSSL::Digest::SHA1.new

_, request_hmac, fullpath = ENV['PATH_INFO'].split('/', 3)
kind, proj, user = fullpath.split('/')
path = [ kind, proj, user ].join('/')
actual_hmac = OpenSSL::HMAC.hexdigest(SHA1, KEY, path)[16, 16]

if request_hmac != actual_hmac
  CGI.new.out('status' => '403') { 'Forbidden' }
  exit
end

ENV['GIT_PROJECT_ROOT'] = CONF['git']
ENV['PATH_INFO'] = "/#{fullpath}" # remove the HMAC from the path
ENV['REMOTE_USER'] = user # enable push
exec([ '/usr/libexec/git-core/git-http-backend', 'git-http-backend' ])

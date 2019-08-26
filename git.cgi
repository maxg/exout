#!/usr/bin/ruby

require 'cgi'
require 'openssl'
require 'yaml'

CONF = YAML.load_file('config/course-setup.yaml')
KEY = IO.read('config/key.txt')

SHA1 = OpenSSL::Digest::SHA1.new
START = 'starting'

_, mode, request_hmac, fullpath = ENV['PATH_INFO'].split('/', 4)
kind, proj, user, etc = fullpath.split('/', 4)
path = [ kind, proj, user ].join('/')
actual_hmac = OpenSSL::HMAC.hexdigest(SHA1, KEY, path)[16, 16]

if request_hmac != actual_hmac
  CGI.new.out('status' => '403') { 'Forbidden' }
  exit
end

ENV['GIT_PROJECT_ROOT'] = CONF['git']
if mode == 'w'
  ENV['PATH_INFO'] = "/#{fullpath}" # remove mode & HMAC from the path
  ENV['REMOTE_USER'] = user # enable push
elsif mode == 'r'
  ENV['PATH_INFO'] = '/' + [ kind, proj, 'exout', START + '.git', etc ].join('/')
else
  CGI.new.out('status' => '404') { 'Not found' }
  exit
end
exec([ '/usr/libexec/git-core/git-http-backend', 'git-http-backend' ])

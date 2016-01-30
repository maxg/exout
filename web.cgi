#!/usr/bin/ruby

require 'cgi'
require 'openssl'
require 'yaml'

CONF = YAML.load_file('config/course-setup.yaml')
KEY = IO.read('config/key.txt')

SHA1 = OpenSSL::Digest::SHA1.new
START = 'starting'
FLAG = 'git-daemon-export-ok'

cgi = CGI.new('html5')

_, kind, proj = cgi.path_info.split('/')

me = ENV['SSL_CLIENT_S_DN_Email'].sub('@MIT.EDU', '')
src = [ CONF['git'], kind, proj, 'exout', START + '.git' ].join('/')
path = [ kind, proj, me + '.git' ].join('/')
dest = [ CONF['git'], path ].join('/')

hmac = OpenSSL::HMAC.hexdigest(SHA1, KEY, path)[16, 16]

cgi.out {
  cgi.html {
    cgi.head {
      cgi.link('href' => "#{CONF['http']}/public/style.css", 'rel' => 'stylesheet')
    } +
    cgi.body {
      if ! (File.directory?(src) && File.file?([ src, FLAG ].join('/')))
        cgi.h2 { 'Error: no such exercise' }
      else
        if ( ! File.directory?(dest)) && ( ! system('cp', '-rT', src, dest))
          cgi.h2 { 'Error copying starting repository' }
        else
          cgi.p { "Your #{proj} Git repository URL is:" } +
          cgi.h2('id' => 'url') { "#{CONF['http']}/git/#{hmac}/#{path}" } +
          cgi.p { 'This is your personal URL. Do not share it.' } +
          (CONF['instructions'] || '') % { :kind => kind, :proj => proj }
        end
      end +
      cgi.script('src' => "#{CONF['http']}/public/script.js")
    }
  }
}

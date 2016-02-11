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

user = ENV['SSL_CLIENT_S_DN_Email'].sub('@MIT.EDU', '')
starting = [ CONF['git'], kind, proj, 'exout', START + '.git' ].join('/')
instructions = [ CONF['git'], kind, proj, 'exout', 'instructions.html' ].join('/')
path = [ kind, proj, user + '.git' ].join('/')
dest = [ CONF['git'], path ].join('/')

hmac = OpenSSL::HMAC.hexdigest(SHA1, KEY, path)[16, 16]

url = "#{CONF['http']}/git/#{hmac}/#{path}"

cgi.out {
  cgi.html {
    cgi.head {
      cgi.link('href' => "#{CONF['http']}/public/style.css", 'rel' => 'stylesheet')
    } +
    cgi.body {
      if ! (File.directory?(starting) && File.file?([ starting, FLAG ].join('/')))
        cgi.h2 { 'Error: no such exercise' }
      else
        if ( ! File.directory?(dest)) && ( ! system('cp', '-rT', starting, dest))
          cgi.h2 { 'Error copying starting repository' }
        else
          cgi.p { "Your #{proj} Git repository URL is:" } +
          cgi.h2 { '&rarr;' + cgi.span('id' => 'url') { url } + '&larr;' } +
          cgi.p { 'This is your personal URL. Do not share it.' } +
          if File.file?(instructions)
            File.read(instructions)
          else
            CONF['instructions'] || ''
          end % { :kind => kind, :proj => proj, :user => user, :url => url }
        end
      end +
      cgi.script('src' => "#{CONF['http']}/public/script.js")
    }
  }
}

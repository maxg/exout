#!/usr/bin/ruby

require 'cgi'
require 'json'
require 'openssl'
require 'yaml'

cgi = CGI.new('html5')

user = begin
  id = cgi.cookies['shibauth'].value[0]
  data = IO.read("../shibauth/sessions/sess_#{id.delete('^0-9a-f')}")
  session = JSON.parse(data)
  session['username'] or raise
rescue
  cgi.out('status' => 302,
          'location' => "/shibauth/auth.php?return_to=#{ENV['REQUEST_URI']}") { '' }
  exit
end

CONF = YAML.load_file('config/course-setup.yaml')
KEY = IO.read('config/key.txt')

SHA1 = OpenSSL::Digest::SHA1.new
START = 'starting'
FLAG = 'git-daemon-export-ok'

_, mode, kind, proj = cgi.path_info.split('/')

starting = [ CONF['git'], kind, proj, 'exout', START + '.git' ].join('/')
valid = File.directory?(starting) && File.file?([ starting, FLAG ].join('/'))
instructions = [ CONF['git'], kind, proj, 'exout', 'instructions.html' ].join('/')
dest = [ CONF['git'], kind, proj, user + '.git' ].join('/')
path = [ user, kind, proj + '.git' ].join('/')

hmac = OpenSSL::HMAC.hexdigest(SHA1, KEY, path)[16, 16]

url = "#{CONF['http']}/git/#{mode}/#{hmac}/#{path}"

cgi.out {
  cgi.html {
    cgi.head {
      cgi.title { if valid then "#{kind}/#{proj}" else 'Error' end + ' - exout' } +
      cgi.link('href' => "#{CONF['http']}/public/style.css", 'rel' => 'stylesheet')
    } +
    cgi.body {
      if ( ! valid)
        cgi.h2 { 'Error: no such exercise' }
      else
        if (mode == 'w') && ( ! File.directory?(dest)) && ( ! system('cp', '-rT', starting, dest))
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

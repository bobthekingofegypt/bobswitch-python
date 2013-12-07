#!/usr/bin/env rake -f

require 'rake/clean'

namespace :test do
    task :test do
        sh "python bobswitch/tests/__main__.py"
    end

    desc "Run unittests and report coverage."
    task :coverage do
        sh "coverage run --source=bobswitch bobswitch/tests/__main__.py"
        sh "coverage report --omit='venv/**,bobswitch/tests/*.py' --fail-under=37"
    end

    # Handy alias for the forgetful:
    task :cover => :coverage

    desc "Generate an HTML report"
    task :html do
        sh "coverage run --source=bobswitch bobswitch/tests/__main__.py"
        sh "coverage html"
        puts "Generated report at htmlcov/index.html"
    end
end


desc "Run unittests"
task :test => 'test:test'


task :default => :test

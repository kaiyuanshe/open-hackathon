class Chef
        module Nexus
                class NexusError < StandardError; end                                                                                                                                                                                         
                class << self
                        def download_url(nexus, group, artifact, packaging, version, repo, classifier = nil)
                                require 'nexus_cli'
                                remote = NexusCli::RemoteFactory.create({:url => nexus, :repository => repo}, true)
                                if classifier != nil 
                                        coordinates = "#{group}:#{artifact}:#{packaging}:#{classifier}:#{version}"
                                else
                                        coordinates = "#{group}:#{artifact}:#{packaging}:#{version}"
                                end 
				Chef::Log.info(coordinates)
                                return remote.get_artifact_download_url(coordinates)
                        end 
                        def get_filename(nexus, group, artifact, packaging, version, repo, classifier = nil)
                                require 'nexus_cli'
                                remote = NexusCli::RemoteFactory.create({:url => nexus, :repository => repo}, true)
                                if classifier != nil 
                                        coordinates = "#{group}:#{artifact}:#{packaging}:#{classifier}:#{version}"
                                else
                                        coordinates = "#{group}:#{artifact}:#{packaging}:#{version}"
                                end 
                                response        = remote.get_artifact_info(coordinates)
                                doc             = REXML::Document.new(response)
                                return File.basename(doc.root.elements["data"].elements["repositoryPath"].text).to_s
                        end 
                end 
        end 
end


uwsgi "toto" do
  parameters "uwsgi" => { "master" => "true", "treads" => "20", "chdir" => "/srv" }
end

# Copyright (c) Microsoft Open Technologies (Shanghai) Co. Ltd.  All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


def assert(actual, expected)
    throw "Error: expected '#{expected}'' but is '#{actual}'" if actual != expected
end

def test(name)
    begin
        yield
    rescue Exception => e
        Chef::Log.error("[FAIL] #{name}. Error message #{e}")
        raise
    end
    Chef::Log.info "[OK]  #{name}."
end

test 'Expect get databag_item attributes' do
    assert node[:databag_item][:secret_source], 'none'
end

test 'Expect get simple attribute from environment' do
    assert node['from_env_1'], 'from_env_value_1'
    assert node[:from_env_1], 'from_env_value_1'
end

test 'Expect get simple attribute from databag' do
    assert databag_item['key1'], 'value1'
    assert databag_item[:key1], 'value1'
end

test 'Expect get simple data bag attributes with node interface' do
    assert node['key1'], 'value1'
    assert node[:key1], 'value1'
end

test 'Expect get array from environment' do
    assert node['from_env_2'], %w(from_env_value_2_1 from_env_value_2_2)
    assert node[:from_env_2], %w(from_env_value_2_1 from_env_value_2_2)
end

test 'Expect get array from databag' do
    assert databag_item['key2'], %w(value2_1 value2_2)
    assert databag_item[:key2], %w(value2_1 value2_2)
end

test 'Expect get array from databag with node interface' do
    assert node['key2'], %w(value2_1 value2_2)
    assert node[:key2], %w(value2_1 value2_2)
end

test 'Expect get simple object from environment' do
    assert node['from_env_3'], {'from_env_3_1' => 'from_env_value_3_1'}
    assert node[:from_env_3], {'from_env_3_1' => 'from_env_value_3_1'}
end

test 'Expect get simple object from databag' do
    assert databag_item['key3'], {'key3_1' => 'value3_1'}
    assert databag_item[:key3], {'key3_1' => 'value3_1'}
end

test 'Expect get simple object from databag with node interface' do
    assert node['key3'], {'key3_1' => 'value3_1'}
    assert node[:key3], {'key3_1' => 'value3_1'}
end

test 'Expect get embedded simple attribute from env' do
    assert node['key4']['from_env_4_1'], 'from_env_value4_1'
    assert node[:key4][:from_env_4_1], 'from_env_value4_1'
end

test 'Expect get embedded simple attribute from databag_item' do
    assert databag_item['key4']['key4_1'], 'value4_1'
    assert databag_item[:key4][:key4_1], 'value4_1'
end

test 'Expect get embedded simple attribute from databag_item with node interface' do
    assert node['key4']['key4_1'], 'value4_1'
    assert node[:key4][:key4_1], 'value4_1'
end

test 'Expect get embedded array from environment' do
    assert node['key4']['from_env_4_2'], %w(from_env_value4_2_1 from_env_value4_2_2)
    assert node[:key4][:from_env_4_2], %w(from_env_value4_2_1 from_env_value4_2_2)
end

test 'Expect get embedded array from databag' do
    assert databag_item['key4']['key4_2'], %w(value4_2_1 value4_2_2)
    assert databag_item[:key4][:key4_2], %w(value4_2_1 value4_2_2)
end

test 'Expect get embedded array from databag with node interface' do
    assert node['key4']['key4_2'], %w(value4_2_1 value4_2_2)
    assert node[:key4][:key4_2], %w(value4_2_1 value4_2_2)
end

test 'Expect get embedded object from environment' do
    assert node['key4']['from_env_4_3']['from_env_4_3_1'], 'from_env_value4_3_1'
    assert node['key4']['from_env_4_3'][:from_env_4_3_1], 'from_env_value4_3_1'
    assert node['key4'][:from_env_4_3]['from_env_4_3_1'], 'from_env_value4_3_1'
    assert node['key4'][:from_env_4_3][:from_env_4_3_1], 'from_env_value4_3_1'
    assert node[:key4]['from_env_4_3']['from_env_4_3_1'], 'from_env_value4_3_1'
    assert node[:key4]['from_env_4_3'][:from_env_4_3_1], 'from_env_value4_3_1'
    assert node[:key4][:from_env_4_3]['from_env_4_3_1'], 'from_env_value4_3_1'
    assert node[:key4][:from_env_4_3][:from_env_4_3_1], 'from_env_value4_3_1'
end

test 'Expect get embedded object from databag' do
    assert databag_item['key4']['key4_3']['key4_3_1'], 'value4_3_1'
    assert databag_item['key4']['key4_3'][:key4_3_1], 'value4_3_1'
    assert databag_item['key4'][:key4_3]['key4_3_1'], 'value4_3_1'
    assert databag_item['key4'][:key4_3][:key4_3_1], 'value4_3_1'
    assert databag_item[:key4]['key4_3']['key4_3_1'], 'value4_3_1'
    assert databag_item[:key4]['key4_3'][:key4_3_1], 'value4_3_1'
    assert databag_item[:key4][:key4_3]['key4_3_1'], 'value4_3_1'
    assert databag_item[:key4][:key4_3][:key4_3_1], 'value4_3_1'
end

test 'Expect get embedded object from databag with node interface' do
    assert node['key4']['key4_3']['key4_3_1'], 'value4_3_1'
    assert node['key4']['key4_3'][:key4_3_1], 'value4_3_1'
    assert node['key4'][:key4_3]['key4_3_1'], 'value4_3_1'
    assert node['key4'][:key4_3][:key4_3_1], 'value4_3_1'
    assert node[:key4]['key4_3']['key4_3_1'], 'value4_3_1'
    assert node[:key4]['key4_3'][:key4_3_1], 'value4_3_1'
    assert node[:key4][:key4_3]['key4_3_1'], 'value4_3_1'
    assert node[:key4][:key4_3][:key4_3_1], 'value4_3_1'
end

test 'Expect get boolean value from environment' do
    assert node[:from_env_5], false
    assert node['from_env_5'], false

    assert node[:from_env_6], true
    assert node['from_env_6'], true
end

test 'Expect get boolean value from databag' do
    assert databag_item[:key5], false
    assert databag_item['key5'], false

    assert databag_item[:key6], true
    assert databag_item['key6'], true
end

test 'Expect get boolean value from databag with node interface' do
    assert node[:key5], false
    assert node['key5'], false

    assert node[:key6], true
    assert node['key6'], true
end

test 'Expect get embedded boolean value from environment' do
    assert node[:key7][:from_env_7_1], true
    assert node[:key7]['from_env_7_1'], true
    assert node['key7'][:from_env_7_1], true
    assert node['key7']['from_env_7_1'], true

    assert node[:key7][:from_env_7_2], false
    assert node[:key7]['from_env_7_2'], false
    assert node['key7'][:from_env_7_2], false
    assert node['key7']['from_env_7_2'], false
end

test 'Expect get embedded boolean value from databag' do
    assert databag_item[:key7][:from_databag_7_1], true
    assert databag_item[:key7]['from_databag_7_1'], true
    assert databag_item['key7'][:from_databag_7_1], true
    assert databag_item['key7']['from_databag_7_1'], true

    assert databag_item[:key7][:from_databag_7_2], false
    assert databag_item[:key7]['from_databag_7_2'], false
    assert databag_item['key7'][:from_databag_7_2], false
    assert databag_item['key7']['from_databag_7_2'], false
end

test 'Expect get embedded boolean value from databag with node interface' do
    assert node[:key7][:from_databag_7_1], true
    assert node[:key7]['from_databag_7_1'], true
    assert node['key7'][:from_databag_7_1], true
    assert node['key7']['from_databag_7_1'], true

    assert node[:key7][:from_databag_7_2], false
    assert node[:key7]['from_databag_7_2'], false
    assert node['key7'][:from_databag_7_2], false
    assert node['key7']['from_databag_7_2'], false
end

test 'Expect value in databag to override value in environment' do
    assert node[:key8], 'value_from_databag'
    assert node['key8'], 'value_from_databag'

    assert databag_item[:key8], 'value_from_databag'
    assert databag_item['key8'], 'value_from_databag'
end

test 'Expect deep merge of databag and env' do
  assert node[:key9]['key9.1'], 'value_from_databag_9.1'
  assert databag_item[:key9]['key9.1'], 'value_from_databag_9.1'

  assert databag_item[:key9]['key9.2'], nil
  assert node[:key9]['key9.2']['key9.2.1'], 'value_from_env_9.2.1'
end
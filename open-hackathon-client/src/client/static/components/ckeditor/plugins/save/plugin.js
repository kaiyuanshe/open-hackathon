CKEDITOR.plugins.registered['save'] = {
  init: function(editor) {
    var command = editor.addCommand('save', {
      modes: {
        wysiwyg: 1,
        source: 1
      },
      readOnly: 1,
      exec: function(editor) {
        editor.fire('save');
      }
    });

    editor.ui.addButton('Save', {
      label: editor.lang.save,
      command: 'save',
      toolbar: 'clipboard,0'
    });
  }
};

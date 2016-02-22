(function() {

  CKEDITOR.plugins.add('save', {
    hidpi: true,
    init: function(editor) {
      if (editor.blockless)
        return;
      var command = editor.addCommand('save', {
        readOnly: 1,
        preserveState: true,
        editorFocus: false,
        exec: function(editor) {
          editor.fire('save');
        }
      });

      editor.ui.addButton('Save', {
        label: editor.lang.save,
        command: 'save',
        toolbar: 'clipboard,0'
      });

      if (editor.contextMenu) {
        editor.contextMenu.addListener(function(element) {
          if (!element || element.isReadOnly())
            return null;
        });
      }
    }
  });

})();

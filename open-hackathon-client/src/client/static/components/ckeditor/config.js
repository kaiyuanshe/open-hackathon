/**
 * @license Copyright (c) 2003-2016, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */



CKEDITOR.editorConfig = function(config) {
  // Define changes to default configuration here.
  // For complete reference see:
  // http://docs.ckeditor.com/#!/api/CKEDITOR.config
  config.extraPlugins = 'save,div,colordialog,liststyle,font,colorbutton,showblocks,justify,video,sourcedialog';
  // config.protectedSource.push(/<video[\s|\S]*video>/g);
  // config.removePlugins = 'iframe,video';
  // The toolbar groups arrangement, optimized for two toolbar rows.
  config.language = 'zh-cn';

  config.allowedContent = true;

  config.toolbarGroups = [{
    name: 'clipboard',
    groups: ['save', 'clipboard', 'undo']
  }, {
    name: 'links'
  }, {
    name: 'insert'
  }, {
    name: 'forms'
  }, {
    name: 'others'
  }, {
    name: 'basicstyles',
    groups: ['basicstyles', 'cleanup']
  }, {
    name: 'paragraph',
    groups: ['list', 'indent', 'blocks', 'bidi']
  }, {
    name: 'align'
  }, {
    name: 'styles'
  }, {
    name: 'colors'
  }, {
    name: 'tools'
  }, {
    name: 'document',
    groups: ['mode', 'document', 'doctools']
  }];

  config.contentsLangDirection = '';
  // Remove some buttons provided by the standard plugins, which are
  // not needed in the Standard(s) toolbar.
  config.removeButtons = 'Underline,Subscript,Superscript';

  // Set the most common block elements.
  //config.format_tags = 'p;h1;h2;h3;pre';

  // Simplify the dialog windows.
  config.removeDialogTabs = 'image:advanced;link:advanced';

  config.div_wrapTable = true;

  config.inlinecancel = {
    onCancel: function(editor) {
      console.log('cancel', editor);
    }
  };

  config.enterMode = CKEDITOR.ENTER_BR;
  config.shiftEnterMode = CKEDITOR.ENTER_P;

};
// CKEDITOR.on('instanceReady', function(ev) {
//   with(ev.editor.dataProcessor.writer) {
//     setRules("p", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("h1", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("h2", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("h3", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("h4", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("h5", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("div", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("table", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("tr", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("td", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("iframe", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("li", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("ul", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//     setRules("ol", {
//       indent: false,
//       breakAfterOpen: false,
//       breakBeforeClose: false
//     });
//   }
// });

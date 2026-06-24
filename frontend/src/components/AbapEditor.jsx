import React from 'react'
import Editor from '@monaco-editor/react'

// Define resaltado mínimo de ABAP la primera vez que se monta Monaco.
function registerAbap(monaco) {
  if (monaco._abapRegistered) return
  monaco._abapRegistered = true
  monaco.languages.register({ id: 'abap' })
  monaco.languages.setMonarchTokensProvider('abap', {
    ignoreCase: true,
    keywords: [
      'REPORT', 'DATA', 'TYPES', 'CONSTANTS', 'FIELD-SYMBOLS', 'TABLES', 'PARAMETERS',
      'SELECT', 'FROM', 'INTO', 'WHERE', 'ENDSELECT', 'LOOP', 'AT', 'ENDLOOP', 'IF', 'ELSEIF',
      'ELSE', 'ENDIF', 'CASE', 'WHEN', 'ENDCASE', 'DO', 'ENDDO', 'WHILE', 'ENDWHILE',
      'FORM', 'ENDFORM', 'PERFORM', 'FUNCTION', 'ENDFUNCTION', 'CALL', 'METHOD', 'METHODS',
      'CLASS', 'ENDCLASS', 'PUBLIC', 'PRIVATE', 'PROTECTED', 'SECTION', 'DEFINITION',
      'IMPLEMENTATION', 'CREATE', 'OBJECT', 'TRY', 'CATCH', 'ENDTRY', 'RAISE', 'EXCEPTION',
      'MODIFY', 'INSERT', 'UPDATE', 'DELETE', 'COMMIT', 'ROLLBACK', 'WORK', 'MOVE',
      'WRITE', 'READ', 'TABLE', 'APPEND', 'CLEAR', 'REFRESH', 'FREE', 'AUTHORITY-CHECK',
      'FOR', 'ALL', 'ENTRIES', 'INNER', 'JOIN', 'ON', 'GROUP', 'BY', 'ORDER', 'UP', 'TO', 'ROWS',
      'BEGIN', 'OF', 'END', 'WITH', 'KEY', 'TYPE', 'LIKE', 'STANDARD', 'SORTED', 'HASHED',
      'RETURNING', 'IMPORTING', 'EXPORTING', 'CHANGING', 'VALUE', 'REF', 'ASSIGN', 'ASSIGNING',
    ],
    tokenizer: {
      root: [
        [/^\*.*$/, 'comment'],
        [/".*$/, 'comment'],
        [/'[^']*'/, 'string'],
        [/\b\d+\b/, 'number'],
        [/[a-z_]\w*/i, { cases: { '@keywords': 'keyword', '@default': 'identifier' } }],
      ],
    },
  })
}

export default function AbapEditor({ value, onChange, height = '420px', readOnly = false, language = 'abap' }) {
  return (
    <div className="overflow-hidden rounded-lg border border-ink-700">
      <Editor
        height={height}
        language={language}
        theme="vs-dark"
        value={value}
        onChange={onChange}
        beforeMount={registerAbap}
        options={{
          readOnly,
          fontSize: 13,
          minimap: { enabled: false },
          fontFamily: 'JetBrains Mono, Consolas, monospace',
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
        }}
      />
    </div>
  )
}

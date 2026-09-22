# Contracts are assumptions. The analyzer does not verify their implementations.
SINKS = {'payment.execute': ('P1', 'P3'), 'db.mutate': ('P1', 'P3'),
         'fs.write': ('P1', 'P3'), 'external_tool': ('P1', 'P2', 'P3'),
         'external_llm': ('P2',)}
BOUNDARIES = {'validate': 'validation', 'sanitize': 'validation',
              'authorize': 'authorization', 'human_approve': 'authorization'}
SOURCES = {'llm': 'LLM', 'external_read': 'external',
           'user_input': 'user', 'sensitive_data': 'local-sensitive'}

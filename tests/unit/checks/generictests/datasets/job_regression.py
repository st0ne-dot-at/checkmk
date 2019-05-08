# yapf: disable


checkname = 'job'


info = [
    ['NODE1', '==>', 'SHREK', '<=='],
    ['NODE1', 'start_time', '1547301201'],
    ['NODE1', 'exit_code', '0'],
    ['NODE1', 'real_time', '2:00.00'],
    ['NODE1', 'user_time', '1.00'],
    ['NODE1', 'system_time', '0.00'],
    ['NODE1', 'reads', '0'],
    ['NODE1', 'writes', '0'],
    ['NODE1', 'max_res_kbytes', '1234'],
    ['NODE1', 'avg_mem_kbytes', '1'],
    ['NODE1', 'invol_context_switches', '12'],
    ['NODE1', 'vol_context_switches', '23'],
    ['NODE1', '==>', 'SNOWWHITE', '<=='],
    ['NODE1', 'start_time', '1557301201'],
    ['NODE1', 'exit_code', '1'],
    ['NODE1', 'real_time', '6:00.00'],
    ['NODE1', 'user_time', '0.00'],
    ['NODE1', 'system_time', '0.00'],
    ['NODE1', 'reads', '0'],
    ['NODE1', 'writes', '0'],
    ['NODE1', 'max_res_kbytes', '2224'],
    ['NODE1', 'avg_mem_kbytes', '0'],
    ['NODE1', 'invol_context_switches', '1'],
    ['NODE1', 'vol_context_switches', '2'],
    ['NODE1', '==>', 'SNOWWHITE.running', '<=='],
    ['NODE1', 'start_time', '1557301261'],
]


discovery = {
    '': [
        ('SHREK', {}),
        ('SNOWWHITE', {}),
    ],
}


checks = {
    '': [
        ('SHREK', {'age': (0, 0)}, [
            (0, '[NODE1] Exit-Code: 0, Started: 2019-01-12 14:53:21, Real-Time: 120 s,'
                ' User-Time: 1.00 s, System-Time: 0.00 s, Filesystem Reads: 0,'
                ' Filesystem Writes: 0, Max. Memory: 1.23 MB, Avg. Memory: 1.00 kB,'
                ' Vol. Context Switches: 23, Invol. Context Switches: 12', [
                    ('start_time', 1547301201),
                    ('real_time', 120.0),
                    ('user_time', 1.00),
                    ('system_time', 0.0),
                    ('reads', 0),
                    ('writes', 0),
                    ('max_res_bytes', 1234000),
                    ('avg_mem_bytes', 1000),
                    ('vol_context_switches', 23),
                    ('invol_context_switches', 12),
                ]),
        ]),
        ('SNOWWHITE', {'age': (0, 0)}, [
            (0, '[NODE1] Currently running (Started: 2019-05-08 09:41:01)', [
                ]),
        ]),
    ],
}

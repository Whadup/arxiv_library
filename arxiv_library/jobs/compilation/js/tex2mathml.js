#! /usr/bin/env node

/*************************************************************************
 *
 *  tex2mml
 *
 *  Uses MathJax to convert a TeX or LaTeX string to a MathML string.
 *
 * ----------------------------------------------------------------------
 *
 *  Copyright (c) 2014 The MathJax Consortium
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

const katex = require('katex');
const process = require('process');

var stdin = process.stdin,
    stdout = process.stdout,
    stderr = process.stderr,
    inputChunks = [];

stdin.resume();
stdin.setEncoding('utf8');

stdin.on('data', function (chunk) {
    // stderr.write(chunk);
    inputChunks.push(chunk);
});

stdin.on('end', function () {
    var inputJSON = inputChunks.join(),
        parsedData = JSON.parse(inputJSON),
        output = [];
    preamble = parsedData.preamble;
    for(var i=0; i<parsedData.sections.length;i++)
    {
        for(j=0; j < parsedData.sections[i].equations.length; j++)
        {
            eq = parsedData.sections[i].equations[j];
            latex = preamble + "\n" + eq.latex;
            try {
                var mml = katex.renderToString(latex,
                    {
                        output:"mathml",
                        throwOnError:true,
                        strict:"ignore",
                    });
                parsedData.sections[i].equations[j].mathml = mml;
                // process.stdout.write("\n");
                // '<span class="katex">...</span>'
            } catch (e) {
                if (e instanceof katex.ParseError) {
                    // KaTeX can't parse the expression
                    html = ("Error in LaTeX:" + e.message)
                        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    process.stderr.write(html);
                }
                else {
                    process.stderr.write(e.message.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"));
                }
            }
        }
    }
    var write = stdout.write(JSON.stringify(parsedData, null, '    '), () => {
        process.exit(0);//console.log('The data has been flushed');
    });
});

// try {
//     var mml = katex.renderToString(argv._[0],
//         {
//             output:"mathml",
//             throwOnError:true,
//             strict:"ignore",
//         });
//     process.stdout.write(mml);
//     process.stdout.write("\n");
//     // '<span class="katex">...</span>'
// } catch (e) {
//     if (e instanceof katex.ParseError) {
//         // KaTeX can't parse the expression
//         html = ("Error in LaTeX:" + e.message)
//             .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
//         process.stderr.write(html);
//         process.exit(1);
//     } else {
//         throw e;  // other error
//         process.exit(1);
//     }
// }
// process.exit(0);

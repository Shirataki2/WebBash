import Vue from 'vue'
import VueCodeMirror from 'vue-codemirror';
import 'codemirror/lib/codemirror.css'

import "codemirror/mode/shell/shell.js";
import "codemirror/addon/edit/closebrackets.js";
import "codemirror/addon/edit/trailingspace.js";
import "codemirror/addon/edit/matchbrackets.js";

import "codemirror/theme/material.css";
import "codemirror/theme/mdn-like.css";


Vue.use(VueCodeMirror, {});

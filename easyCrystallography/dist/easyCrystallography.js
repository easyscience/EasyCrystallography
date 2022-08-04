/*!
 * Copyright (c) 2012 - 2022, Anaconda, Inc., and Bokeh Contributors
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 * 
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * Neither the name of Anaconda nor the names of any contributors
 * may be used to endorse or promote products derived from this software
 * without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.
 */
(function(root, factory) {
  factory(root["Bokeh"], undefined);
})(this, function(Bokeh, version) {
  let define;
  return (function(modules, entry, aliases, externals) {
    const bokeh = typeof Bokeh !== "undefined" && (version != null ? Bokeh[version] : Bokeh);
    if (bokeh != null) {
      return bokeh.register_plugin(modules, entry, aliases);
    } else {
      throw new Error("Cannot find Bokeh " + version + ". You have to load it prior to loading plugins.");
    }
  })
({
"f492373223": /* index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const easyCrystallographyExtensions = (0, tslib_1.__importStar)(require("153c19733b") /* ./graphics/bokeh_extensions/ */);
    exports.easyCrystallographyExtensions = easyCrystallographyExtensions;
    const base_1 = require("@bokehjs/base");
    (0, base_1.register_models)(easyCrystallographyExtensions);
},
"153c19733b": /* graphics/bokeh_extensions/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    var ngl_viewer_1 = require("584f8ea9f3") /* ./ngl_viewer */;
    __esExport("NGLViewer", ngl_viewer_1.NGLViewer);
},
"584f8ea9f3": /* graphics/bokeh_extensions/ngl_viewer.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const html_box_1 = require("@bokehjs/models/layouts/html_box");
    class NGLViewerView extends html_box_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            this.connect(this.model.properties.object.change, this.updateStage);
            this.connect(this.model.properties.extension.change, this.updateStage);
            this.connect(this.model.properties.representation.change, this.updateStage);
            this.connect(this.model.properties.color_scheme.change, this.updateParameters);
            this.connect(this.model.properties.custom_color_scheme.change, this.updateParameters);
            this.connect(this.model.properties.effect.change, this.updateEffect);
            this.connect(this.model.properties.background.change, this.setBackgroundcolor);
        }
        render() {
            super.render();
            this.el.id = "viewport";
            const wn = window;
            const ngl = wn.NGL;
            this._stage = new ngl.Stage(this.el);
            this.setBackgroundcolor();
            const stage = this._stage;
            this.updateStage();
            window.addEventListener("resize", function () {
                stage.handleResize();
            }, false);
        }
        setBackgroundcolor() {
            console.log(this.model.background);
            this._stage.setParameters({ backgroundColor: this.model.background });
        }
        after_layout() {
            super.after_layout();
            this._stage.handleResize();
        }
        updateEffect() {
            if (this.model.effect === "spin") {
                this._stage.setSpin(true);
            }
            else if (this.model.effect === "rock") {
                this._stage.setRock(true);
            }
            else {
                this._stage.setSpin(false);
                this._stage.setRock(false);
            }
        }
        getParameters() {
            if (this.model.color_scheme === "custom") {
                var list = this.model.custom_color_scheme;
                var scheme = NGL.ColormakerRegistry.addSelectionScheme(list, "new scheme");
                return { color: scheme };
            }
            else {
                return { colorScheme: this.model.color_scheme };
            }
        }
        updateParameters() {
            const parameters = this.getParameters();
            try {
                this._stage.compList[0].reprList[0].setParameters(parameters);
            }
            catch (e) {
                console.log(e);
            }
        }
        updateStage() {
            const model = this.model;
            this._stage.removeAllComponents();
            if (model.object === "") {
                return;
            }
            const parameters = this.getParameters();
            function finish(o) {
                o.addRepresentation(model.representation, parameters);
                o.autoView();
            }
            if (model.extension !== "") {
                this._stage.loadFile(new Blob([model.object], { type: 'text/plain' }), { ext: model.extension }).then(finish);
            }
            else if (model.object.includes("://")) {
                this._stage.loadFile(model.object).then(finish);
            }
            else {
                this._stage.loadFile("rcsb://" + model.object).then(finish);
            }
            // this.updateColor()
            this.updateEffect();
        }
    }
    exports.NGLViewerView = NGLViewerView;
    NGLViewerView.__name__ = "NGLViewerView";
    class NGLViewer extends html_box_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
        static init_NGLViewer() {
            this.prototype.default_view = NGLViewerView;
            this.define(({ String, Any }) => ({
                object: [String, "<button style='width:100%'>Click Me</button>"],
                extension: [String, "cif"],
                representation: [String, "ribbon"],
                color_scheme: [String, "chainid"],
                custom_color_scheme: [Any, "chainid"],
                effect: [String, ""],
                // background:               [ String, "white"], // This crashes the code :/
            }));
            this.override({
                height: 400,
                width: 600
            });
        }
    }
    exports.NGLViewer = NGLViewer;
    NGLViewer.__name__ = "NGLViewer";
    NGLViewer.__module__ = "easyCrystallography.graphics.bokeh_extensions.ngl_viewer";
    NGLViewer.init_NGLViewer();
},
}, "f492373223", {"index":"f492373223","graphics/bokeh_extensions/index":"153c19733b","graphics/bokeh_extensions/ngl_viewer":"584f8ea9f3"}, {});});
//# sourceMappingURL=easyCrystallography.js.map

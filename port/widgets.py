# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import hippo
import gobject
import logging
import math

from sugar.graphics import style
from sugar.graphics import palette
from sugar.graphics import toolbutton
from sugar.graphics import radiotoolbutton
from sugar.graphics import icon
from sugar.graphics import toggletoolbutton
from sugar.graphics import combobox
from sugar.graphics import roundbox

def labelize(text, widget):
    box = hippo.CanvasBox()
    box.props.spacing = style.DEFAULT_SPACING

    text = hippo.CanvasText(text=text)
    text.props.color = style.COLOR_SELECTION_GREY.get_int()
    if gtk.widget_get_default_direction() == gtk.TEXT_DIR_RTL:
        text.props.xalign = hippo.ALIGNMENT_END
    else:
        text.props.xalign = hippo.ALIGNMENT_START
    box.append(text)

    box.append(widget, hippo.PACK_EXPAND)

    return box

class Entry(hippo.CanvasWidget):
    def __init__(self, text=None, frame_color=style.COLOR_WHITE.get_gdk_color(),
            **kwargs):
        hippo.CanvasWidget.__init__(self, **kwargs)

        self.entry = gtk.Entry()
        self.entry.modify_bg(gtk.STATE_INSENSITIVE, frame_color)

        self.props.widget = self.entry

        if text:
            self.text = text

    def get_text(self):
        return self.entry.props.text

    def set_text(self, value):
        self.entry.props.text = value

    text = gobject.property(type=str, setter=set_text, getter=get_text)
    text = property(get_text, set_text)

class TextView(hippo.CanvasWidget):
    def __init__(self, text=None, **kwargs):
        hippo.CanvasWidget.__init__(self, **kwargs)

        self.view = gtk.TextView()
        self.view.props.left_margin = style.DEFAULT_SPACING
        self.view.props.right_margin = style.DEFAULT_SPACING
        self.view.props.wrap_mode = gtk.WRAP_WORD
        self.view.props.accepts_tab = False
        self.view.show()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_shadow_type(gtk.SHADOW_OUT)
        scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(self.view)

        self.props.widget = scrolled_window

        if text:
            self.text = text

    def get_text(self):
        return self.view.props.buffer.props.text

    def set_text(self, value):
        self.view.props.buffer.props.text = value or ''

    text = gobject.property(type=str, setter=set_text, getter=get_text)
    text = property(get_text, set_text)

class Image(hippo.CanvasWidget):
    def __init__(self, pal=None, tooltip=None, pixbuf=None, **kwargs):
        self.image = gtk.Image()
        self._invoker = palette.CanvasInvoker()

        hippo.CanvasBox.__init__(self, widget=self.image)

        self._invoker._position_hint = self._invoker.AT_CURSOR
        self._invoker.attach(self)

        self.palette_class = None

        self.connect('destroy', self._destroy_cb)

        if pal:
            self.palette = pal
        if tooltip:
            self.tooltip = tooltip
        if pixbuf:
            self.pixbuf = pixbuf

    def _destroy_cb(self, widget):
        if self._invoker is not None:
            self._invoker.detach()

    def create_palette(self):
        if self.palette_class is None:
            return None
        if isinstance(self.palette_class, tuple):
            return self.palette_class[0](*self.palette_class[1:])
        else:
            return self.palette_class()

    def get_palette(self):
        return self._invoker.palette

    def set_palette(self, palette):
        self._invoker.palette = palette

    palette = gobject.property(type=object,
            setter=set_palette, getter=get_palette)
    palette = property(get_palette, set_palette)

    def get_tooltip(self):
        return self._invoker.palette and self._invoker.palette.primary_text

    def set_tooltip(self, text):
        self.set_palette(palette.Palette(text))

    tooltip = gobject.property(type=str, setter=set_tooltip, getter=get_tooltip)
    tooltip = property(get_tooltip, set_tooltip)

    def set_pixbuf(self, value):
        self.image.set_from_pixbuf(value)
        self.props.box_width = value.get_width()
        self.props.box_height = value.get_height()

    pixbuf = gobject.property(type=object, setter=set_pixbuf, getter=None)
    pixbuf = property(None, set_pixbuf)

class ToolButton(toolbutton.ToolButton):
    def __init__(self,
            icon_name,
            size=gtk.ICON_SIZE_SMALL_TOOLBAR,
            padding=None,
            **kwargs):

        toolbutton.ToolButton.__init__(self, **kwargs)

        image = icon.Icon(icon_name=icon_name, icon_size=size)
        image.show()

        # The alignment is a hack to work around gtk.ToolButton code
        # that sets the icon_size when the icon_widget is a gtk.Image
        alignment = gtk.Alignment(0.5, 0.5)
        alignment.show()
        alignment.add(image)

        self.set_icon_widget(alignment)

        sizes = { gtk.ICON_SIZE_SMALL_TOOLBAR: style.SMALL_ICON_SIZE,
                  gtk.ICON_SIZE_LARGE_TOOLBAR: style.STANDARD_ICON_SIZE }

        if padding is not None and sizes.has_key(size):
            button_size = sizes[size] + style.DEFAULT_SPACING + padding
            self.set_size_request(button_size, button_size)

class RadioToolButton(radiotoolbutton.RadioToolButton):
    def __init__(self,
            icon_name,
            size=gtk.ICON_SIZE_SMALL_TOOLBAR,
            padding=None,
            **kwargs):

        radiotoolbutton.RadioToolButton.__init__(self, **kwargs)

        image = icon.Icon(icon_name=icon_name, icon_size=size)
        image.show()

        # The alignment is a hack to work around gtk.ToolButton code
        # that sets the icon_size when the icon_widget is a gtk.Image
        alignment = gtk.Alignment(0.5, 0.5)
        alignment.show()
        alignment.add(image)

        self.set_icon_widget(alignment)

        sizes = { gtk.ICON_SIZE_SMALL_TOOLBAR: style.SMALL_ICON_SIZE,
                  gtk.ICON_SIZE_LARGE_TOOLBAR: style.STANDARD_ICON_SIZE }

        if padding is not None and sizes.has_key(size):
            button_size = sizes[size] + style.DEFAULT_SPACING + padding
            self.set_size_request(button_size, button_size)

class ToolWidget(gtk.ToolItem):
    def __init__(self, widget):
        gtk.ToolItem.__init__(self)
        self.add(widget)
        widget.show()

class ToggleToolButton(toggletoolbutton.ToggleToolButton):
    def __init__(self, named_icon=None, tooltip=None, palette=None, **kwargs):
        toggletoolbutton.ToggleToolButton.__init__(self, named_icon, **kwargs)

        if tooltip:
            self.set_tooltip(tooltip)
        if palette:
            self.set_palette(palette)

class Palette(palette.Palette):
    def __init__(self, **kwargs):
        palette.Palette.__init__(self, **kwargs)

    def popup(self, immediate=False, state=None):
        if not self.props.invoker:
            if _none_invoker.palette:
                _none_invoker.palette.popdown(immediate=True)
            _none_invoker.palette = self
            self.props.invoker = _none_invoker
        palette.Palette.popup(self, immediate, state)

class _NoneInvoker(palette.Invoker):
    def __init__(self):
        palette.Invoker.__init__(self)
        self._position_hint = palette.Invoker.AT_CURSOR

    def get_rect(self):
        return gtk.gdk.Rectangle(0, 0, 0, 0)

    def get_toplevel(self):
        return None

_none_invoker  = _NoneInvoker()

class ComboBox(combobox.ComboBox):
    def __init__(self, **kwargs):
        combobox.ComboBox.__init__(self, **kwargs)

    def select(self, id=None, name=None):
        if id is not None:
            column = 0
            value = id
        elif name is not None:
            column = 1
            value = name
        else:
            return

        for i, item in enumerate(self.get_model()):
            if item[column] != value:
                continue
            self.set_active(i)
            break

    def append_item(self, action_id, text, icon_name=None, file_name=None):
        item = self._item_new(action_id, text, icon_name, file_name)
        self.get_model().append(item)

    def set_item(self, action_id, text=None, icon_name=None, file_name=None):
        for i, value in enumerate(self.get_model()):
            if value[0] == action_id:
                item = self._item_new(action_id, text, icon_name, file_name)
                iter = self.get_model().iter_nth_child(None, i)
                if text is not None:
                    self.get_model().set(iter, 1, item[1])
                if icon_name is not None or file_name is not None:
                    self.get_model().set(iter, 2, item[2])
                return True
        return False

    def _item_new(self, action_id, text, icon_name, file_name):
        if not self._icon_renderer and (icon_name or file_name):
            self._icon_renderer = gtk.CellRendererPixbuf()

            settings = self.get_settings()
            w, h = gtk.icon_size_lookup_for_settings(
                                            settings, gtk.ICON_SIZE_MENU)
            self._icon_renderer.props.stock_size = max(w, h)

            self.pack_start(self._icon_renderer, False)
            self.add_attribute(self._icon_renderer, 'pixbuf', 2)

        if not self._text_renderer and text:
            self._text_renderer = gtk.CellRendererText()
            self.pack_end(self._text_renderer, True)
            self.add_attribute(self._text_renderer, 'text', 1)

        if icon_name or file_name:
            if text:
                size = gtk.ICON_SIZE_MENU
            else:
                size = gtk.ICON_SIZE_LARGE_TOOLBAR
            width, height = gtk.icon_size_lookup(size)

            if icon_name:
                file_name = self._get_real_name_from_theme(icon_name, size)

            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(
                                                file_name, width, height)
        else:
            pixbuf = None

        return (action_id, text, pixbuf, False)

class ToolComboBox(gtk.ToolItem):
    __gproperties__ = {
        'label-text' : (str, None, None, None,
                        gobject.PARAM_WRITABLE),
    }

    def __init__(self, combo=None, **kwargs):
        self.label = None
        self._label_text = ''

        gobject.GObject.__init__(self, **kwargs)

        self.set_border_width(style.DEFAULT_PADDING)

        hbox = gtk.HBox(False, style.DEFAULT_SPACING)

        self.label = gtk.Label(self._label_text)
        hbox.pack_start(self.label, False)
        self.label.show()

        if combo:
            self.combo = combo
        else:
            self.combo = ComboBox()

        hbox.pack_start(self.combo)
        self.combo.show()

        self.add(hbox)
        hbox.show()

    def do_set_property(self, pspec, value):
        if pspec.name == 'label-text':
            self._label_text = value
            if self.label:
                self.label.set_text(self._label_text)

class CanvasRoundBox(roundbox.CanvasRoundBox):
    def __init__(self, radius=style.zoom(10), **kwargs):
        hippo.CanvasBox.__init__(self, **kwargs)
        self.set_radius(radius)

    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        self.props.border_left = radius
        self.props.border_right = radius

    radius = property(get_radius, set_radius)

    def do_paint_background(self, cr, damaged_box):
        [width, height] = self.get_allocation()

        cr.rectangle(0, 0, width, height)
        hippo.cairo_set_source_rgba32(cr, self.props.background_color)
        cr.fill()

        x = self.props.border_top/2
        y = self.props.border_top/2
        width -= self.props.border_top
        height -= self.props.border_top

        cr.move_to(x + self._radius, y)
        cr.arc(x + width - self._radius, y + self._radius,
               self._radius, math.pi * 1.5, math.pi * 2)
        cr.arc(x + width - self._radius, x + height - self._radius,
               self._radius, 0, math.pi * 0.5)
        cr.arc(x + self._radius, y + height - self._radius,
               self._radius, math.pi * 0.5, math.pi)
        cr.arc(x + self._radius, y + self._radius, self._radius,
               math.pi, math.pi * 1.5)

        hippo.cairo_set_source_rgba32(cr, self.props.background_color)
        cr.fill_preserve()

        # TODO: we should be more consistent here with the border properties.
        if self.props.border_color:
            hippo.cairo_set_source_rgba32(cr, self.props.border_color)
            cr.set_line_width(self.props.border_top)
            cr.stroke()

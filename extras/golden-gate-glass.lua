-- Golden Gate theme: Liquid Glass blur, soft shadows, hairline borders and
-- macOS-like rounded corners. Installed by extras/install-glass.sh.
-- Remove the matching require line from ~/.config/hypr/hyprland.lua to disable.

hl.config({
  general = {
    border_size = 1,
  },

  decoration = {
    rounding = 10,
    rounding_power = 3.0,

    shadow = {
      enabled = true,
      range = 28,
      render_power = 3,
      color = "rgba(0000008c)",
      color_inactive = "rgba(00000059)",
    },

    -- Frosted, slightly vibrant blur behind translucent surfaces only;
    -- opaque app windows are unaffected.
    blur = {
      enabled = true,
      size = 10,
      passes = 3,
      noise = 0.015,
      contrast = 1.0,
      brightness = 0.9,
      vibrancy = 0.25,
      vibrancy_darkness = 0.2,
      new_optimizations = true,
      xray = false,
      popups = true,
      popups_ignorealpha = 0.2,
    },
  },
})

-- Glass shell surfaces. ignore_alpha keeps the faint dim scrim behind menus
-- and the launcher from being blurred, so only the cards frost.
hl.layer_rule({
  match = { namespace = "^omarchy-(bar|menu|clipboard|emojis|notifications|osd|polkit|reminders|keyboard-panel|network-qr)$" },
  blur = true,
  ignore_alpha = 0.3,
})

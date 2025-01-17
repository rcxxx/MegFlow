/**
 * \file flow-rs/examples/megflow_run.rs
 * MegFlow is Licensed under the Apache License, Version 2.0 (the "License")
 *
 * Copyright (c) 2019-2021 Megvii Inc. All rights reserved.
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT ARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 */
use clap::{App, Arg};
use flow_rs::loader;
use flow_rs::prelude::*;
use std::env::current_dir;
use std::path::PathBuf;

#[flow_rs::rt::main]
async fn main() {
    let matches = App::new("megflow_run")
        .version("1.0.0")
        .author("megengine <megengine@megvii.com>")
        .arg(
            Arg::new("DEBUG")
                .long("debug")
                .value_name("DEBUG")
                .about("Debug mode")
                .multiple_occurrences(false)
                .required(false),
        )
        .arg(
            Arg::new("DUMP")
                .long("dump")
                .about("The path to dump graph")
                .multiple_occurrences(false)
                .required(false),
        )
        .arg(
            Arg::new("MODULE_PATH")
                .long("module")
                .short('m')
                .value_name("MODULE_PATH")
                .about("Module path")
                .multiple_occurrences(false)
                .required(false),
        )
        .arg(
            Arg::new("PLUGIN_PATH")
                .long("plugin")
                .short('p')
                .value_name("PLUGIN_PATH")
                .about("Plugin path")
                .multiple_occurrences(false)
                .required(false),
        )
        .arg(
            Arg::new("CONFIG_PATH")
                .long("config")
                .short('c')
                .value_name("CONFIG_PATH")
                .about("Config path")
                .multiple_occurrences(false)
                .required(false),
        )
        .get_matches();

    let dump = matches.is_present("DUMP");
    let module = matches
        .value_of("MODULE_PATH")
        .unwrap_or(current_dir().unwrap().to_str().unwrap())
        .parse::<PathBuf>()
        .unwrap();
    let plugin = matches
        .value_of("PLUGIN_PATH")
        .map(|s| s.parse::<PathBuf>().unwrap())
        .unwrap();
    let config = matches
        .value_of("CONFIG_PATH")
        .map(|s| s.parse::<PathBuf>().unwrap())
        .unwrap_or_else(|| {
            let mut config = std::fs::canonicalize(&plugin).unwrap();
            let dirname = config.file_name().unwrap();
            let config_name = format!("{}.toml", dirname.to_str().unwrap());
            config.push(config_name);
            config
        });

    flow_plugins::export();
    ctrlc::set_handler(|| unsafe { libc::_exit(0) }).expect("Error setting Ctrl-C handler");

    if dump {
        let mut dump_path = config.clone();
        dump_path.pop();
        let file_stem = config.file_stem().unwrap().to_str().unwrap();
        dump_path.push(format!("{}.png", file_stem));
        log::info!("dump path: {:?}", dump_path);
        std::env::set_var("MEGFLOW_DUMP", dump_path.to_str().unwrap());
    }

    let plugin_cfg = loader::LoaderConfig {
        module_path: module,
        plugin_path: plugin,
        ty: loader::PluginType::Python,
    };

    let cfg = std::fs::read_to_string(config).unwrap();

    if let Some(dbg_port) = matches.value_of("DEBUG") {
        let dbg_port: u16 = dbg_port.parse().unwrap();
        let server = flow_rs::DebugServer::new(cfg.clone(), dbg_port);
        flow_rs::rt::task::spawn(async move {
            server.listen().await;
        });
    }

    let mut graph = load(Some(plugin_cfg), cfg.as_str()).unwrap();
    let graph_handle = graph.start();
    graph.stop();
    graph_handle.await
}

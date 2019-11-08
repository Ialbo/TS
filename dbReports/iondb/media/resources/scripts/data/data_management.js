function _get_query_string(val){
    val = val || "";
    if ($.isArray(val)){
        return val.join(",")
    }
    return val;
}

function filter(e){
	  e.preventDefault();
	  e.stopPropagation();

	  var id = $(e.currentTarget).data('id');
	  /* calculate the date range for the '__range' operator */
	  var daterange = '';
	  var _daterange = $("#rangeA_"+id).data("daterange");
	  if (_daterange) {
		var start = _daterange.start.clone();
		var end = _daterange.end.clone().addHours(23).addMinutes(59);
		daterange = start.toString('yyyy-MM-dd HH:mm') + "," + end.toString('yyyy-MM-dd HH:mm');
	  }

	  $("#grid_"+id).data("kendoGrid").dataSource.filter([
		  {
			  field: "timeStamp",
			  operator: "__range",
			  value: daterange
		  },
          {
			  field: "search_name",
			  operator: "",
			  value: $("#search_text_"+id).val()
		  },
          {
			field: "sigproc_filter",
			operator: "",
			value: _get_query_string($("#filter_sigproc_"+id).val())
		  },
          {
			field: "basecall_filter",
			operator: "",
			value: _get_query_string($("#filter_basecall_"+id).val())
		  },
          {
			field: "output_filter",
			operator: "",
			value: _get_query_string($("#filter_output_"+id).val())
		  },
          {
			field: "misc_filter",
			operator: "",
			value: _get_query_string($("#filter_misc_"+id).val())
		  }
	  ]);
}

function show_ack(data){
    if(data.sigproc_keep=='true'){
        return false;
    } else if (data.sigproc_state == 'Notified' || data.sigproc_state == 'Selected' || data.sigproc_state == 'Acknowledged'){
        return true;
    }
    return false;
}

function refresh_grid_timer(source, refresh){
	var grid = $(source).data('kendoGrid');
	clearInterval(grid.update_timer);
	if (refresh)
		grid.update_timer = setInterval(function(){ grid.dataSource.read(); }, 10000);
}

function refresh_grid_timeout(source, refresh){
    if (refresh){
        var grid = $(source).data('kendoGrid');
        setTimeout(function(){ grid.dataSource.read(); }, 10000);
    }
}

function showModal(elem, modal_id){
	var url = $(elem).attr('href');
	console.log('showModal', modal_id, url);
	$( 'body #'+modal_id ).remove();
	$.get(url, function(data) {
	   $('body').append(data);
	   $( "#"+modal_id ).modal("show");
	});
}

$(document).ready(function () {

	$('#data_import').click(function(e){
		e.preventDefault();
		$.get($(this).attr('href'), function(data) {
			$('body').append(data);
			$( "#modal_import_data" ).modal("show");
		 }).done(function(){
			$('body #modal_import_data').on('modal_import_data_done', function (e, data) {
				console.log('modal_import_data_done', data);
				$('#data_import_status').html(data).show();
				refreshKendoGrid("#dmjobs_grid");
			});
		});
	});

	$("#enable_archive").change(function(){
		var enabled = $(this).is(':checked');
		$.ajax({
			type: "PATCH",
			dataType: 'json',
			url: "/rundb/api/v1/globalconfig/1/",
			data: '{"auto_archive_enable":'+enabled+'}',
			contentType: 'application/json'
		}).done(function(data) {
			if (enabled) {
				var log_entry = 'ENABLED Data Management automatic action';
			} else {
				var log_entry = 'DISABLED Data Management automatic action';
			}
			$.post("/data/datamanagement/dmconfig_log/", {log: log_entry});
		});
	});

	$("#dm_config_log").click(function(e){
		e.preventDefault();
		showModal(this, 'modal_event_log');
	});

	$('[name=rangeA]').each(function(){ $(this).daterangepicker($.DateRangePickerSettings.get()); });
	$('.rangeA').change(function (e) { filter(e); });
	$('.search_text').change(function (e) { filter(e); });
	$('.filter_state').change(function (e) { filter(e); });
	$('.clear_filters').click(function (e) {
		var id = $(e.currentTarget).data('id');
		$("#rangeA_"+id).removeData("daterange");
		$("#rangeA_"+id).trigger('change');
		$('#search_bar_'+id).find('input').each(function(){$(this).val(''); });
		$('#search_bar_'+id+' .selectpicker').selectpicker('deselectAll');
		filter(e);
	});
});
